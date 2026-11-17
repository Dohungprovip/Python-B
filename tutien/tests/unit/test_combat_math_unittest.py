"""Demo 1 - unittest (thư viện chuẩn): unittest.TestCase, setUp, assert*, subTest.

Đối tượng test: src/core/combat_math.py::giam_theo_phong_thu  (sát thương = raw² / (raw + def)).
Chạy riêng:  python -m unittest tests.unit.test_combat_math_unittest -v
Hoặc bằng pytest:  pytest tests/unit/test_combat_math_unittest.py -v
"""
import unittest

from src.core.combat_math import giam_theo_phong_thu


class GiamTheoPhongThuTest(unittest.TestCase):
    def setUp(self):
        # setUp chạy trước MỖI test: chuẩn bị dữ liệu dùng chung
        self.raw = 100

    def test_khong_phong_thu_giu_nguyen_sat_thuong(self):
        self.assertEqual(giam_theo_phong_thu(self.raw, 0), 100)

    def test_phong_thu_bang_sat_thuong_con_50_phan_tram(self):
        self.assertEqual(giam_theo_phong_thu(self.raw, 100), 50)

    def test_phong_thu_gap_doi_con_mot_phan_ba(self):
        self.assertEqual(giam_theo_phong_thu(self.raw, 200), 33)

    def test_khong_bao_gio_mien_nhiem(self):
        # phòng thủ cực lớn vẫn gây tối thiểu 1 sát thương
        self.assertGreaterEqual(giam_theo_phong_thu(1, 10**9), 1)

    def test_sat_thuong_khong_hop_le_tra_ve_1(self):
        for raw in (0, -5, None):
            with self.subTest(raw=raw):
                self.assertEqual(giam_theo_phong_thu(raw, 50), 1)

    def test_phong_thu_am_duoc_coi_la_0(self):
        self.assertEqual(giam_theo_phong_thu(100, -999), 100)

    def test_ket_qua_la_so_nguyen(self):
        self.assertIsInstance(giam_theo_phong_thu(123.7, 45.2), int)

    def test_phong_thu_cang_cao_sat_thuong_cang_thap(self):
        values = [giam_theo_phong_thu(1000, d) for d in (0, 100, 500, 2000)]
        self.assertEqual(values, sorted(values, reverse=True))


if __name__ == "__main__":
    unittest.main()
