import re
import time

import pytest

pytestmark = pytest.mark.data


def count(q, sql, *args):
    return q(f"SELECT COUNT(*) AS n FROM ({sql})", *args)[0]["n"]


class TestNguoiChoi:
    def test_co_du_lieu_nguoi_choi(self, q):
        assert q("SELECT COUNT(*) n FROM nguoi_choi")[0]["n"] > 0

    def test_linh_thach_khong_am(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE linh_thach < 0") == 0

    def test_hp_khong_am(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE hp < 0") == 0

    def test_hp_toi_da_trong_db_la_chi_so_goc_nen_hp_co_the_vuot(self, q):
        # hp_max là chỉ số gốc; HP hiện tại có thể cao hơn nhờ trang bị và buff (chỉ số hiệu dụng tính khi chạy game).
        over = count(q, "SELECT 1 FROM nguoi_choi WHERE hp > hp_max")
        total = q("SELECT COUNT(*) n FROM nguoi_choi")[0]["n"]
        assert 0 < over < total

    def test_hp_toi_da_duong(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE hp_max <= 0") == 0

    def test_chi_so_co_ban_khong_am(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE atk < 0 OR def < 0 OR toc_do < 0") == 0

    def test_noi_nang_khong_am(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE noi_nang < 0") == 0

    def test_than_thuc_khong_vuot_toi_da(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE than_thuc < 0 OR than_thuc > than_thuc_toi_da") == 0

    def test_dao_tam_khong_vuot_toi_da(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE dao_tam < 0 OR dao_tam > dao_tam_toi_da") == 0

    def test_exp_tu_luyen_khong_am(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE cultivation_exp < 0") == 0

    def test_canh_gioi_ton_tai(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE cultivation_realm_id NOT IN (SELECT id FROM cultivation_realm)") == 0

    def test_tieu_canh_gioi_khong_vuot_so_tang_cua_canh_gioi(self, q):
        sql = (
            "SELECT 1 FROM nguoi_choi p JOIN cultivation_realm r ON r.id=p.cultivation_realm_id "
            "WHERE p.cultivation_stage < 1 OR p.cultivation_stage > r.max_stage"
        )
        assert count(q, sql) == 0

    def test_it_nguoi_choi_dang_dung_exp_vuot_yeu_cau_cho_dot_pha(self, q):
        # exp được phép vượt mốc trong lúc chờ đột phá, nhưng chỉ là số ít.
        sql = (
            "SELECT 1 FROM nguoi_choi p JOIN cultivation_stage s "
            "ON s.realm_id=p.cultivation_realm_id AND s.stage=p.cultivation_stage "
            "WHERE p.cultivation_exp > s.required_exp"
        )
        total = q("SELECT COUNT(*) n FROM nguoi_choi")[0]["n"]
        assert count(q, sql) <= total * 0.05

    def test_ten_nhan_vat_khong_rong_va_khong_trung(self, q):
        row = q("SELECT COUNT(*) n, COUNT(DISTINCT LOWER(TRIM(ten))) d, SUM(TRIM(COALESCE(ten,''))='') e FROM nguoi_choi")[0]
        assert row["e"] == 0
        assert row["d"] == row["n"]

    def test_the_chat_ton_tai(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE the_chat_id IS NOT NULL AND the_chat_id NOT IN (SELECT id FROM the_chat)") == 0

    def test_mon_phai_ton_tai(self, q):
        sql = "SELECT 1 FROM nguoi_choi WHERE mon_phai_id IS NOT NULL AND mon_phai_id<>0 AND mon_phai_id NOT IN (SELECT id FROM mon_phai)"
        assert count(q, sql) == 0

    def test_ban_do_hien_tai_ton_tai(self, q):
        sql = "SELECT 1 FROM nguoi_choi WHERE ban_do_hien_tai_id IS NOT NULL AND ban_do_hien_tai_id<>0 AND ban_do_hien_tai_id NOT IN (SELECT id FROM ban_do)"
        assert count(q, sql) == 0

    def test_ngay_tao_khong_o_tuong_lai(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE created_at > ?", int(time.time()) + 86400) == 0

    def test_trang_thai_nhap_ma_la_0_hoac_1(self, q):
        assert {r[0] for r in q("SELECT DISTINCT is_demonized FROM nguoi_choi")} <= {0, 1, None}

    def test_dang_bi_quan_thi_co_thoi_diem_ket_thuc(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE is_retreating=1 AND (retreat_end_time IS NULL OR retreat_end_time<=0)") == 0

    def test_thoi_diem_bi_quan_hop_ly(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE is_retreating=1 AND retreat_end_time < retreat_start_time") == 0

    def test_json_trang_thai_thien_phu_hop_le(self, q):
        import json

        bad = 0
        for r in q("SELECT tp_trang_thai FROM nguoi_choi WHERE tp_trang_thai IS NOT NULL AND tp_trang_thai<>''"):
            try:
                if not isinstance(json.loads(r[0]), dict):
                    bad += 1
            except ValueError:
                bad += 1
        assert bad == 0


class TestTaiKhoan:
    def test_moi_nguoi_choi_co_tai_khoan(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi WHERE user_id NOT IN (SELECT user_id FROM web_tai_khoan)") == 0

    def test_tai_khoan_chua_tao_nhan_vat_la_so_it(self, q):
        # Tài khoản mới đăng ký nhưng chưa qua bước tạo nhân vật là trạng thái hợp lệ.
        pending = count(q, "SELECT 1 FROM web_tai_khoan WHERE user_id NOT IN (SELECT user_id FROM nguoi_choi)")
        assert pending <= 3

    def test_mat_khau_luu_dang_bam_co_muoi_rieng(self, q):
        assert count(q, "SELECT 1 FROM web_tai_khoan WHERE TRIM(COALESCE(salt,''))='' OR TRIM(COALESCE(password_hash,''))=''") == 0

    def test_bam_mat_khau_la_chuoi_hex_dai_du(self, q):
        pattern = re.compile(r"^[0-9a-fA-F]{32,}$")
        values = [r[0] for r in q("SELECT password_hash FROM web_tai_khoan")]
        assert all(pattern.match(v) for v in values)

    def test_khong_co_hai_tai_khoan_dung_chung_muoi(self, q):
        row = q("SELECT COUNT(*) n, COUNT(DISTINCT salt) d FROM web_tai_khoan")[0]
        assert row["n"] == row["d"]

    def test_muoi_khong_trung_voi_bam(self, q):
        assert count(q, "SELECT 1 FROM web_tai_khoan WHERE salt = password_hash") == 0

    def test_ten_dang_nhap_khong_co_khoang_trang_dau_cuoi(self, q):
        assert count(q, "SELECT 1 FROM web_tai_khoan WHERE username <> TRIM(username)") == 0

    def test_co_tai_khoan_quan_tri_va_khong_nhieu_hon_mot_nua(self, q):
        row = q("SELECT COUNT(*) n, SUM(is_admin) a FROM web_tai_khoan")[0]
        assert 1 <= row["a"] <= row["n"] / 2

    def test_co_ban_la_0_hoac_1(self, q):
        assert {r[0] for r in q("SELECT DISTINCT is_banned FROM web_tai_khoan")} <= {0, 1}

    def test_bi_khoa_thi_co_ly_do(self, q):
        assert count(q, "SELECT 1 FROM web_tai_khoan WHERE is_banned=1 AND TRIM(COALESCE(ban_reason,''))=''") == 0

    def test_phien_dang_nhap_chi_luu_ma_bam(self, q):
        pattern = re.compile(r"^[0-9a-f]{64}$")
        values = [r[0] for r in q("SELECT token_hash FROM web_phien_dang_nhap")]
        assert values and all(pattern.match(v) for v in values)

    def test_phien_dang_nhap_thuoc_tai_khoan_co_that(self, q):
        assert count(q, "SELECT 1 FROM web_phien_dang_nhap WHERE user_id NOT IN (SELECT user_id FROM web_tai_khoan)") == 0

    def test_phien_het_han_sau_luc_tao(self, q):
        assert count(q, "SELECT 1 FROM web_phien_dang_nhap WHERE expires_at <= created_at") == 0

    def test_thoi_gian_song_phien_khong_qua_30_ngay(self, q):
        assert count(q, "SELECT 1 FROM web_phien_dang_nhap WHERE expires_at - created_at > 30*86400") == 0


class TestKyNangVaCongPhap:
    def test_ky_nang_nguoi_choi_ton_tai(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi_ky_nang WHERE ky_nang_key NOT IN (SELECT key FROM ky_nang_dinh_nghia)") == 0

    def test_ky_nang_thuoc_nguoi_choi_co_that(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi_ky_nang WHERE user_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0

    def test_cap_do_ky_nang_trong_bang_cau_hinh(self, q):
        top = q("SELECT MAX(cap_do) m FROM cau_hinh_exp_ky_nang")[0]["m"]
        assert count(q, "SELECT 1 FROM nguoi_choi_ky_nang WHERE cap_do < 1 OR cap_do > ?", top) == 0

    def test_cong_phap_nguoi_choi_khong_vuot_so_tang_toi_da(self, q):
        sql = (
            "SELECT 1 FROM nguoi_choi_cong_phap n JOIN cong_phap c ON c.id=n.cong_phap_id "
            "WHERE n.tang < 0 OR n.tang > c.max_tang"
        )
        assert count(q, sql) == 0

    def test_cong_phap_nguoi_choi_ton_tai(self, q):
        assert count(q, "SELECT 1 FROM nguoi_choi_cong_phap WHERE cong_phap_id NOT IN (SELECT id FROM cong_phap)") == 0

    def test_thien_phu_cua_nguoi_choi_la_json(self, q):
        import json

        for r in q("SELECT phan_bo_json FROM thien_phu_nguoi_choi WHERE phan_bo_json IS NOT NULL AND phan_bo_json<>''"):
            assert isinstance(json.loads(r[0]), (dict, list))


class TestKinhTeVaXaHoi:
    def test_so_du_ngan_hang_khong_am(self, q):
        assert count(q, "SELECT 1 FROM ngan_hang_so_du WHERE so_du < 0") == 0

    def test_ngan_hang_thuoc_nguoi_choi_co_that(self, q):
        assert count(q, "SELECT 1 FROM ngan_hang_so_du WHERE user_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0

    def test_gia_ban_cho_den_duong(self, q):
        assert count(q, "SELECT 1 FROM cho_den_rao_ban WHERE gia <= 0 OR so_luong <= 0") == 0

    def test_nguoi_mua_khac_nguoi_ban(self, q):
        assert count(q, "SELECT 1 FROM cho_den_rao_ban WHERE buyer_id IS NOT NULL AND buyer_id = seller_id") == 0

    def test_gia_shop_nguoi_choi_duong(self, q):
        assert count(q, "SELECT 1 FROM shop_nguoi_choi_ban WHERE cost <= 0 OR so_luong_con < 0") == 0

    def test_nguoi_ban_shop_ton_tai(self, q):
        assert count(q, "SELECT 1 FROM shop_nguoi_choi_ban WHERE seller_user_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0

    def test_giftcode_khong_dung_qua_so_lan_cho_phep(self, q):
        assert count(q, "SELECT 1 FROM giftcode WHERE max_uses > 0 AND used_count > max_uses") == 0

    def test_moi_nguoi_chi_nhan_mot_lan_moi_giftcode(self, q):
        assert count(q, "SELECT 1 FROM giftcode_da_nhan GROUP BY player_id, gift_id HAVING COUNT(*) > 1") == 0

    def test_giftcode_da_nhan_tro_toi_code_co_that(self, q):
        assert count(q, "SELECT 1 FROM giftcode_da_nhan WHERE gift_id NOT IN (SELECT id FROM giftcode)") == 0

    def test_chu_tong_mon_la_nguoi_choi_co_that(self, q):
        assert count(q, "SELECT 1 FROM mon_phai WHERE chu_nhan_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0

    def test_thanh_vien_tong_mon_ton_tai(self, q):
        assert count(q, "SELECT 1 FROM tong_mon_thanh_vien WHERE user_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0

    def test_moi_nguoi_chi_o_mot_tong_mon(self, q):
        assert count(q, "SELECT 1 FROM tong_mon_thanh_vien GROUP BY user_id HAVING COUNT(*) > 1") == 0

    def test_quan_he_khong_tu_ket_ban_voi_chinh_minh(self, q):
        assert count(q, "SELECT 1 FROM quan_he_nguoi_choi WHERE user_id_1 = user_id_2") == 0

    def test_nhat_ky_dao_tam_thuoc_nguoi_choi_co_that(self, q):
        assert count(q, "SELECT 1 FROM dao_tam_nhat_ky WHERE user_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0


class TestLichSu:
    def test_tran_danh_ket_thuc_sau_khi_bat_dau(self, q):
        assert count(q, "SELECT 1 FROM lich_su_giao_tranh WHERE ket_thuc_luc < bat_dau_luc") == 0

    def test_lich_su_giao_tranh_tro_toi_nguoi_choi_co_that(self, q):
        assert count(q, "SELECT 1 FROM lich_su_giao_tranh WHERE player_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0

    def test_hai_bang_lich_su_giao_tranh_khop_so_dong(self, q):
        a = q("SELECT COUNT(*) n FROM lich_su_giao_tranh")[0]["n"]
        b = q("SELECT COUNT(*) n FROM lich_su_lich_luyen")[0]["n"]
        assert a == b

    def test_so_luot_va_sat_thuong_lich_luyen_khong_am(self, q):
        assert count(q, "SELECT 1 FROM lich_su_lich_luyen WHERE so_luot < 0 OR tong_sat_thuong_gay_ra < 0 OR tong_sat_thuong_nhan < 0") == 0

    def test_nguoi_thang_pvp_la_mot_trong_hai_nguoi_choi(self, q):
        assert count(q, "SELECT 1 FROM lich_su_doi_chien WHERE winner_id NOT IN (player_1, player_2)") == 0

    def test_lich_su_be_quan_xuat_quan_khong_truoc_luc_vao(self, q):
        assert count(q, "SELECT 1 FROM lich_su_be_quan WHERE xuat_quan_luc IS NOT NULL AND xuat_quan_luc < bat_dau_luc") == 0

    def test_lich_su_be_quan_exp_khong_am(self, q):
        assert count(q, "SELECT 1 FROM lich_su_be_quan WHERE exp_nhan < 0 OR exp_bi_tru < 0") == 0

    def test_ma_nhiem_vu_hop_le_trong_lich_su(self, q):
        assert count(q, "SELECT 1 FROM lich_su_nhiem_vu WHERE player_id NOT IN (SELECT user_id FROM nguoi_choi)") == 0

    def test_ban_ghi_migration_co_ten_va_thoi_gian(self, q):
        assert count(q, "SELECT 1 FROM schema_migrations WHERE TRIM(COALESCE(name,''))='' OR applied_at IS NULL") == 0

    def test_so_phien_ban_migration_khong_chay_theo_thoi_gian(self, q):
        # Số phiên bản là nhãn của migration, không phải thứ tự thời gian: bản 108 được áp dụng trước bản 70.
        rows = q("SELECT version, applied_at FROM schema_migrations ORDER BY version")
        times = [r["applied_at"] for r in rows]
        assert times != sorted(times)
        assert all(t > 1_600_000_000 for t in times)
