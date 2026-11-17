import sqlite3
import unittest

from src.core import tribulation_backlash as tb


class BacklashTest(unittest.TestCase):
    def setUp(self):
        self.now = 1_700_000_000
        self.player = {
            "thien_loi_phan_phe_started_at": self.now - 100,
            "thien_loi_phan_phe_until": self.now + 500,
        }

    def test_dang_bi_phan_phe_khi_chua_het_han(self):
        self.assertTrue(tb.backlash_active(self.player, self.now))

    def test_het_han_dung_luc_thi_khong_con_phan_phe(self):
        self.player["thien_loi_phan_phe_until"] = self.now
        self.assertFalse(tb.backlash_active(self.player, self.now))

    def test_thieu_truong_du_lieu_coi_nhu_khong_bi(self):
        for player in ({}, {"thien_loi_phan_phe_until": None}, {"thien_loi_phan_phe_until": 0}):
            with self.subTest(player=player):
                self.assertFalse(tb.backlash_active(player, self.now))
                self.assertEqual(tb.backlash_until(player), 0)

    def test_gia_tri_am_duoc_dua_ve_0(self):
        self.assertEqual(tb.backlash_until({"thien_loi_phan_phe_until": -5}), 0)
        self.assertEqual(tb.backlash_started_at({"thien_loi_phan_phe_started_at": -5}), 0)

    def test_trang_thai_dang_hieu_luc(self):
        status = tb.backlash_status(self.player, self.now)
        self.assertTrue(status["active"])
        self.assertEqual(status["remaining_seconds"], 500)
        self.assertEqual(status["expires_at"], self.now + 500)
        self.assertEqual(status["started_at"], self.now - 100)
        self.assertFalse(status["can_tribulate"])

    def test_trang_thai_sau_khi_het_han_cho_phep_do_kiep(self):
        status = tb.backlash_status(self.player, self.now + 10_000)
        self.assertFalse(status["active"])
        self.assertEqual(status["remaining_seconds"], 0)
        self.assertTrue(status["can_tribulate"])

    def test_phat_phan_tram_khop_he_so_nhan(self):
        status = tb.backlash_status(self.player, self.now)
        self.assertEqual(status["stat_penalty_percent"], round((1 - tb.BACKLASH_STAT_MULTIPLIER) * 100))
        self.assertEqual(status["cultivation_exp_penalty_percent"], round((1 - tb.BACKLASH_EXP_MULTIPLIER) * 100))

    def test_doc_duoc_ca_sqlite_row(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute("CREATE TABLE p (thien_loi_phan_phe_until INTEGER, thien_loi_phan_phe_started_at INTEGER)")
        con.execute("INSERT INTO p VALUES (?, ?)", (self.now + 60, self.now))
        row = con.execute("SELECT * FROM p").fetchone()
        self.assertEqual(tb.backlash_until(row), self.now + 60)
        self.assertTrue(tb.backlash_active(row, self.now))
        con.close()

    def test_row_thieu_cot_tra_ve_mac_dinh(self):
        con = sqlite3.connect(":memory:")
        con.row_factory = sqlite3.Row
        con.execute("CREATE TABLE p (ten TEXT)")
        con.execute("INSERT INTO p VALUES ('a')")
        self.assertEqual(tb.backlash_until(con.execute("SELECT * FROM p").fetchone()), 0)
        con.close()

    def test_hang_so_hop_le(self):
        self.assertLess(tb.BACKLASH_MIN_SECONDS, tb.BACKLASH_MAX_SECONDS)
        self.assertEqual(tb.BACKLASH_MIN_SECONDS, 3 * 3600)
        self.assertEqual(tb.BACKLASH_MAX_SECONDS, 6 * 3600)
        for value in (tb.BACKLASH_STAT_MULTIPLIER, tb.BACKLASH_EXP_MULTIPLIER, tb.BACKLASH_EXP_LOSS_RATE):
            self.assertGreater(value, 0)
            self.assertLess(value, 1)


if __name__ == "__main__":
    unittest.main()
