import pytest

pytestmark = pytest.mark.data


def orphans(q, child_table, child_col, parent_table, parent_col, where="1=1"):
    sql = (
        f'SELECT COUNT(*) AS n FROM "{child_table}" c '
        f'WHERE {where} AND c."{child_col}" IS NOT NULL '
        f'AND c."{child_col}" NOT IN (SELECT "{parent_col}" FROM "{parent_table}" WHERE "{parent_col}" IS NOT NULL)'
    )
    return q(sql)[0]["n"]


FOREIGN_KEYS = [
    ("vat_pham_dinh_nghia", "type", "type_vp", "id_type"),
    ("vat_pham_dinh_nghia", "pham_cap_id", "pham_cap_vat_pham", "id"),
    ("vat_pham_option_mac_dinh", "temp_id", "vat_pham_dinh_nghia", "id_vp"),
    ("vat_pham_option_mac_dinh", "id_chi_so", "vat_pham_chi_so", "id_chi_so"),
    ("quai_ban_do", "quai_id", "quai", "id"),
    ("quai_ban_do", "ban_do_id", "ban_do", "id"),
    ("ban_do", "khu_vuc_id", "khu_vuc", "id"),
    ("ban_do", "the_gioi_id", "the_gioi", "id"),
    ("khu_vuc", "the_gioi_id", "the_gioi", "id"),
    ("cultivation_stage", "realm_id", "cultivation_realm", "id"),
    ("cong_phap_tang", "cong_phap_id", "cong_phap", "id"),
    ("cong_phap_ky_nang", "cong_phap_id", "cong_phap", "id"),
    ("cong_phap_ky_nang", "ky_nang_key", "ky_nang_dinh_nghia", "key"),
    ("ky_nang_hieu_ung", "ky_nang_key", "ky_nang_dinh_nghia", "key"),
    ("linh_thu_ky_nang_map", "linh_thu_id", "linh_thu_dinh_nghia", "id"),
    ("linh_thu_ky_nang_map", "ky_nang_id", "linh_thu_ky_nang", "id"),
    ("linh_thu_dinh_nghia", "pham_cap_id", "pham_cap_vat_pham", "id"),
    ("itemshop", "temp_id", "vat_pham_dinh_nghia", "id_vp"),
    ("cau_hinh_cuong_hoa", "pham_cap_id", "pham_cap_vat_pham", "id"),
    ("cau_hinh_cuong_hoa", "vp_chi_phi_id", "vat_pham_dinh_nghia", "id_vp"),
    ("dan_duoc_cong_thuc", "dan_id", "vat_pham_dinh_nghia", "id_vp"),
    ("thanh_tri", "map_id", "ban_do", "id"),
    ("map_thanh_gan_nhat", "thanh_id", "thanh_tri", "id"),
    ("ky_ngo_lua_chon", "ky_ngo_id", "ky_ngo", "id"),
    ("ky_ngo_ket_qua", "lua_chon_id", "ky_ngo_lua_chon", "id"),
    ("tab_shop", "type_vp_id", "type_vp", "id_type"),
]


KNOWN_ORPHANS = {
    ("thanh_tri", "map_id"): "thanh_tri id 40 và 41 trỏ tới map 138 và 147 không có trong ban_do (phát hiện khi kiểm thử dữ liệu)",
}


def _param(child, col, parent, pcol):
    reason = KNOWN_ORPHANS.get((child, col))
    marks = [pytest.mark.xfail(reason=reason, strict=True)] if reason else []
    return pytest.param(child, col, parent, pcol, id=f"{child}.{col}->{parent}", marks=marks)


@pytest.mark.parametrize("child, col, parent, pcol", [_param(*fk) for fk in FOREIGN_KEYS])
def test_khong_co_ban_ghi_mo_coi(q, child, col, parent, pcol):
    assert orphans(q, child, col, parent, pcol) == 0


UNIQUE_KEYS = [
    ("ky_nang_dinh_nghia", "key"),
    ("vat_pham_dinh_nghia", "key"),
    ("vat_pham_dinh_nghia", "id_vp"),
    ("cong_phap", "key"),
    ("the_chat", "key"),
    ("pham_cap_vat_pham", "key"),
    ("pham_cap_vat_pham", "thu_tu"),
    ("cultivation_realm", "realm_order"),
    ("cultivation_realm", "name"),
    ("linh_thu_dinh_nghia", "key"),
    ("tran_phap", "key"),
    ("ky_ngo", "key"),
    ("quai", "id"),
    ("ban_do", "id"),
    ("web_tai_khoan", "username"),
    ("web_tai_khoan", "user_id"),
    ("nguoi_choi", "user_id"),
    ("nguoi_choi", "ten"),
    ("giftcode", "ten_gift"),
    ("schema_migrations", "version"),
]


@pytest.mark.parametrize("table, col", UNIQUE_KEYS, ids=[f"{t}.{c}" for t, c in UNIQUE_KEYS])
def test_khoa_la_duy_nhat_va_khong_rong(q, table, col):
    row = q(f'SELECT COUNT(*) AS n, COUNT("{col}") AS filled, COUNT(DISTINCT "{col}") AS d FROM "{table}"')[0]
    assert row["n"] > 0
    assert row["filled"] == row["n"], "có giá trị NULL"
    assert row["d"] == row["n"], "có giá trị trùng"


def test_ten_vat_pham_va_ky_nang_khong_rong(q):
    assert q("SELECT COUNT(*) n FROM ky_nang_dinh_nghia WHERE TRIM(COALESCE(ten,''))=''")[0]["n"] == 0
    assert q("SELECT COUNT(*) n FROM quai WHERE TRIM(COALESCE(ten,''))=''")[0]["n"] == 0


def test_ky_nang_tien_quyet_ton_tai(q):
    n = q(
        "SELECT COUNT(*) n FROM cong_phap_ky_nang WHERE prerequisite_key IS NOT NULL AND TRIM(prerequisite_key)<>'' "
        "AND prerequisite_key NOT IN (SELECT key FROM ky_nang_dinh_nghia)"
    )[0]["n"]
    assert n == 0


def test_moi_cong_phap_co_it_nhat_mot_tang(q):
    n = q("SELECT COUNT(*) n FROM cong_phap WHERE id NOT IN (SELECT cong_phap_id FROM cong_phap_tang)")[0]["n"]
    assert n == 0


def test_so_tang_cong_phap_khong_vuot_max_tang(q):
    n = q(
        "SELECT COUNT(*) n FROM cong_phap cp WHERE (SELECT COUNT(*) FROM cong_phap_tang t WHERE t.cong_phap_id=cp.id) > cp.max_tang"
    )[0]["n"]
    assert n == 0


class TestKyNang:
    def test_thoi_gian_hoi_chieu_khong_am(self, q):
        assert q("SELECT COUNT(*) n FROM ky_nang_dinh_nghia WHERE hoi_chieu < 0")[0]["n"] == 0

    def test_he_so_sat_thuong_duong(self, q):
        assert q("SELECT COUNT(*) n FROM ky_nang_dinh_nghia WHERE kha_nang=0 AND thong_so <= 0")[0]["n"] == 0

    def test_canh_gioi_yeu_cau_nam_trong_15_canh_gioi(self, q):
        assert q("SELECT COUNT(*) n FROM ky_nang_dinh_nghia WHERE canh_gioi_yeu_cau < 0 OR canh_gioi_yeu_cau > 15")[0]["n"] == 0

    def test_loai_kha_nang_hop_le(self, q):
        values = {r["kha_nang"] for r in q("SELECT DISTINCT kha_nang FROM ky_nang_dinh_nghia")}
        assert values <= {0, 1, 2, 3, 4, 5}

    def test_ti_le_hieu_ung_trong_khoang_0_den_1(self, q):
        assert q("SELECT COUNT(*) n FROM ky_nang_hieu_ung WHERE ti_le < 0 OR ti_le > 1")[0]["n"] == 0


class TestVatPham:
    def test_ti_le_roi_khong_am(self, q):
        assert q("SELECT COUNT(*) n FROM vat_pham_dinh_nghia WHERE drop_rate < 0")[0]["n"] == 0

    def test_do_tinh_khiet_khong_am(self, q):
        assert q("SELECT COUNT(*) n FROM vat_pham_dinh_nghia WHERE do_tinh_khiet < 0")[0]["n"] == 0

    def test_ngan_sach_pham_cap_thu_tu_tang_dan_theo_id(self, q):
        rows = q("SELECT id, thu_tu FROM pham_cap_vat_pham ORDER BY id")
        assert [r["thu_tu"] for r in rows] == sorted(r["thu_tu"] for r in rows)

    def test_he_so_suc_manh_tang_dan_theo_pham_cap(self, q):
        values = [r["he_so_suc_manh"] for r in q("SELECT he_so_suc_manh FROM pham_cap_vat_pham ORDER BY thu_tu")]
        assert values == sorted(values) and len(set(values)) == len(values)

    def test_pham_cap_cang_cao_cang_hiem(self, q):
        values = [r["ti_le_xuat_hien"] for r in q("SELECT ti_le_xuat_hien FROM pham_cap_vat_pham ORDER BY thu_tu")]
        assert values == sorted(values, reverse=True)

    def test_vat_pham_ban_trong_shop_co_gia_duong(self, q):
        assert q("SELECT COUNT(*) n FROM itemshop WHERE cost <= 0")[0]["n"] == 0

    def test_ban_ve_va_nguyen_lieu_luyen_khi_hop_le(self, q):
        assert q("SELECT COUNT(*) n FROM luyen_khi_cong_thuc WHERE so_luong_min > so_luong_max")[0]["n"] == 0
        assert q("SELECT COUNT(*) n FROM luyen_khi_cong_thuc WHERE ti_le_thanh_cong < 0 OR ti_le_thanh_cong > 100")[0]["n"] == 0

    def test_cong_thuc_luyen_dan_hop_le(self, q):
        assert q("SELECT COUNT(*) n FROM dan_duoc_cong_thuc WHERE so_dan_min > so_dan_max")[0]["n"] == 0
        assert q("SELECT COUNT(*) n FROM dan_duoc_cong_thuc WHERE ti_le_no_lo < 0")[0]["n"] == 0


class TestCuongHoa:
    def test_cap_cuong_hoa_lien_tuc_theo_pham_cap(self, q):
        for r in q("SELECT pham_cap_id, MIN(cap) lo, MAX(cap) hi, COUNT(*) n FROM cau_hinh_cuong_hoa GROUP BY pham_cap_id"):
            assert r["n"] == r["hi"] - r["lo"] + 1, f"phẩm cấp {r['pham_cap_id']} thiếu cấp"

    def test_ti_le_thanh_cong_trong_khoang_hop_le(self, q):
        assert q("SELECT COUNT(*) n FROM cau_hinh_cuong_hoa WHERE ti_le_thanh_cong < 0 OR ti_le_thanh_cong > 100")[0]["n"] == 0

    def test_ti_le_giam_dan_khi_len_cap(self, q):
        for pc in [r[0] for r in q("SELECT DISTINCT pham_cap_id FROM cau_hinh_cuong_hoa")]:
            rates = [r["ti_le_thanh_cong"] for r in q("SELECT ti_le_thanh_cong FROM cau_hinh_cuong_hoa WHERE pham_cap_id=? ORDER BY cap", pc)]
            assert rates == sorted(rates, reverse=True), f"phẩm cấp {pc}: tỉ lệ không giảm dần"

    def test_chi_phi_tang_dan_khi_len_cap(self, q):
        for pc in [r[0] for r in q("SELECT DISTINCT pham_cap_id FROM cau_hinh_cuong_hoa")]:
            cost = [r["so_luong_chi_phi"] for r in q("SELECT so_luong_chi_phi FROM cau_hinh_cuong_hoa WHERE pham_cap_id=? ORDER BY cap", pc)]
            assert cost == sorted(cost), f"phẩm cấp {pc}: chi phí không tăng dần"

    def test_he_so_chi_so_tang_dan_khi_len_cap(self, q):
        for pc in [r[0] for r in q("SELECT DISTINCT pham_cap_id FROM cau_hinh_cuong_hoa")]:
            mult = [r["he_so_tang_chi_so"] for r in q("SELECT he_so_tang_chi_so FROM cau_hinh_cuong_hoa WHERE pham_cap_id=? ORDER BY cap", pc)]
            assert mult == sorted(mult) and mult[0] > 1.0

    def test_so_luong_chi_phi_duong(self, q):
        assert q("SELECT COUNT(*) n FROM cau_hinh_cuong_hoa WHERE so_luong_chi_phi <= 0")[0]["n"] == 0


class TestQuaiVaBanDo:
    def test_chi_so_quai_hop_le(self, q):
        assert q("SELECT COUNT(*) n FROM quai WHERE hp <= 0")[0]["n"] == 0
        assert q("SELECT COUNT(*) n FROM quai WHERE atk < 0 OR def < 0 OR toc_do < 0")[0]["n"] == 0

    def test_loai_quai_la_0_1_hoac_2(self, q):
        assert {r["loai"] for r in q("SELECT DISTINCT loai FROM quai")} <= {0, 1, 2}

    def test_so_luong_quai_moi_ban_do_hop_le(self, q):
        assert q("SELECT COUNT(*) n FROM quai_ban_do WHERE so_luong_toi_thieu > so_luong_toi_da")[0]["n"] == 0
        assert q("SELECT COUNT(*) n FROM quai_ban_do WHERE ti_le_xuat_hien < 0")[0]["n"] == 0

    def test_canh_gioi_ban_do_thap_nhat_khong_lon_hon_cao_nhat(self, q):
        assert q("SELECT COUNT(*) n FROM ban_do WHERE canh_gioi_thap_nhat > canh_gioi_cao_nhat")[0]["n"] == 0

    def test_ban_do_truoc_ton_tai(self, q):
        assert orphans(q, "ban_do", "ban_do_truoc_id", "ban_do", "id") == 0

    def test_ban_do_khong_tro_ve_chinh_no(self, q):
        assert q("SELECT COUNT(*) n FROM ban_do WHERE ban_do_truoc_id = id")[0]["n"] == 0


class TestCauHinhKhac:
    def test_than_hon_cap_lien_tuc(self, q):
        caps = [r["cap"] for r in q("SELECT cap FROM than_hon_cau_hinh ORDER BY cap")]
        assert caps == list(range(1, len(caps) + 1))

    def test_than_hon_yeu_cau_tang_dan_den_cap_cuoi(self, q):
        rows = q("SELECT * FROM than_hon_cau_hinh ORDER BY cap")
        for col in ("exp_can", "linh_thach_can", "than_thuc_toi_da", "atk_percent"):
            values = [r[col] for r in rows[:-1]] if col in ("exp_can", "linh_thach_can") else [r[col] for r in rows]
            assert values == sorted(values), f"{col} không tăng dần"

    def test_than_hon_cap_cuoi_khong_con_yeu_cau_len_cap(self, q):
        last = q("SELECT * FROM than_hon_cau_hinh ORDER BY cap DESC LIMIT 1")[0]
        assert last["exp_can"] == 0 and last["linh_thach_can"] == 0

    def test_thien_kiep_phu_toan_bo_15_canh_gioi(self, q):
        orders = [r["realm_order"] for r in q("SELECT realm_order FROM thien_kiep_cau_hinh ORDER BY realm_order")]
        assert len(orders) == len(set(orders))
        assert set(orders) <= set(range(1, 16))

    def test_thien_kiep_co_it_nhat_mot_dot_sam(self, q):
        assert q("SELECT COUNT(*) n FROM thien_kiep_cau_hinh WHERE waves < 1")[0]["n"] == 0

    def test_quy_doi_tien_te_duong(self, q):
        assert q("SELECT COUNT(*) n FROM cau_hinh_quy_doi_tien_te WHERE gia_tri_linh_thach <= 0")[0]["n"] == 0

    def test_dung_mot_tien_te_chinh(self, q):
        assert q("SELECT COUNT(*) n FROM tien_te_cau_hinh WHERE la_linh_thach_chinh=1")[0]["n"] == 1

    def test_cau_hinh_key_khong_trung(self, q):
        row = q("SELECT COUNT(*) n, COUNT(DISTINCT key) d FROM cau_hinh")[0]
        assert row["n"] == row["d"]

    def test_so_luong_diem_danh_30_ngay(self, q):
        days = [r["ngay_thu"] for r in q("SELECT ngay_thu FROM diem_danh_phan_thuong ORDER BY ngay_thu")]
        assert days == list(range(1, 31))

    def test_dung_mot_dong_cau_hinh_admin(self, q):
        assert q("SELECT COUNT(*) n FROM server_admin_config")[0]["n"] == 1

    def test_phan_tram_exp_may_chu_khong_am(self, q):
        assert q("SELECT COUNT(*) n FROM server_admin_config WHERE exp_percent < 0")[0]["n"] == 0
