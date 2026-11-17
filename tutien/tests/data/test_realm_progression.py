import pytest

pytestmark = pytest.mark.data


@pytest.fixture(scope="module")
def realms(q):
    return q("SELECT * FROM cultivation_realm ORDER BY realm_order")


@pytest.fixture(scope="module")
def stages_by_realm(q):
    result = {}
    for r in q("SELECT * FROM cultivation_stage ORDER BY realm_id, stage"):
        result.setdefault(r["realm_id"], []).append(r)
    return result


def test_co_dung_15_canh_gioi(realms):
    assert len(realms) == 15


def test_thu_tu_canh_gioi_lien_tuc_tu_1_den_15(realms):
    assert [r["realm_order"] for r in realms] == list(range(1, 16))


def test_id_canh_gioi_trung_thu_tu(realms):
    assert [r["id"] for r in realms] == [r["realm_order"] for r in realms]


def test_so_tieu_canh_gioi_khop_bang_stage(realms, stages_by_realm):
    for r in realms:
        assert len(stages_by_realm[r["id"]]) == r["max_stage"], r["name"]


def test_tong_so_tieu_canh_gioi_la_77(stages_by_realm):
    assert sum(len(v) for v in stages_by_realm.values()) == 77


def test_cac_tang_danh_so_lien_tuc_tu_1(stages_by_realm):
    for realm_id, rows in stages_by_realm.items():
        assert [s["stage"] for s in rows] == list(range(1, len(rows) + 1)), realm_id


def test_exp_can_tang_ngat_trong_moi_canh_gioi(stages_by_realm):
    for realm_id, rows in stages_by_realm.items():
        values = [s["required_exp"] for s in rows]
        assert values == sorted(set(values)), realm_id


def test_exp_can_tang_ngat_giua_cac_canh_gioi(stages_by_realm):
    last = 0
    for realm_id in sorted(stages_by_realm)[:-1]:
        first = stages_by_realm[realm_id][0]["required_exp"]
        assert first > last, f"cảnh giới {realm_id} bắt đầu thấp hơn cảnh giới trước"
        last = stages_by_realm[realm_id][-1]["required_exp"]


def test_canh_gioi_cuoi_dung_0_lam_gia_tri_khong_gioi_han(stages_by_realm):
    top = stages_by_realm[max(stages_by_realm)]
    assert [s["required_exp"] for s in top] == [0]


def test_khoang_exp_moi_lan_tu_luyen_hop_le(stages_by_realm):
    for realm_id, rows in stages_by_realm.items():
        if realm_id == max(stages_by_realm):
            continue
        for s in rows:
            assert 0 < s["exp_min"] <= s["exp_max"] < s["required_exp"]


def test_ti_le_dot_pha_khong_tang_theo_canh_gioi(realms):
    rates = [r["breakthrough_rate"] for r in realms]
    assert rates == sorted(rates, reverse=True)


def test_ti_le_dot_pha_trong_khoang_0_den_1(realms):
    assert all(0 < r["breakthrough_rate"] <= 1 for r in realms)


def test_canh_gioi_dau_dot_pha_chac_chan(realms):
    assert realms[0]["breakthrough_rate"] == 1.0


def test_ti_le_do_kiep_khong_tang_theo_canh_gioi(realms):
    rates = [r["tribulation_rate"] for r in realms]
    assert rates == sorted(rates, reverse=True)
    assert all(0 <= x <= 1 for x in rates)


def test_phat_that_bai_dot_pha_la_ti_le_hop_le(realms):
    assert all(0 <= r["failure_exp_loss_percent"] <= 1 for r in realms)


def test_ten_canh_gioi_khong_trung_va_khong_rong(realms):
    names = [r["name"] for r in realms]
    assert all(n and n.strip() for n in names) and len(set(names)) == 15


def test_hai_canh_gioi_cuoi_chi_co_mot_tang(realms):
    assert [r["max_stage"] for r in realms[-2:]] == [1, 1]


def test_so_tang_giam_dan_theo_canh_gioi(realms):
    stages = [r["max_stage"] for r in realms]
    assert stages == sorted(stages, reverse=True)


@pytest.mark.xfail(
    strict=True,
    reason="Phát hiện khi kiểm thử dữ liệu: 11/15 tên trong thien_kiep_cau_hinh (Luyện Khí, Trúc Cơ, Kim Đan...) "
    "không khớp tên trong cultivation_realm (Ly Hợp, Chân Nguyên, Thần Du...).",
)
def test_ten_canh_gioi_khop_gia_tri_thien_kiep(q, realms):
    names = {r["realm_order"]: r["name"] for r in realms}
    mismatched = [
        row["realm_order"]
        for row in q("SELECT realm_order, ten FROM thien_kiep_cau_hinh")
        if names.get(row["realm_order"]) != row["ten"]
    ]
    assert mismatched == []


def test_dot_kiep_thien_kiep_khong_vuot_moc_canh_gioi(q):
    assert q("SELECT COUNT(*) n FROM thien_kiep_cau_hinh WHERE realm_order NOT BETWEEN 1 AND 15")[0]["n"] == 0


def test_sat_thuong_goc_thien_kiep_tang_theo_canh_gioi(q):
    values = [r["base_damage_percent"] for r in q("SELECT base_damage_percent FROM thien_kiep_cau_hinh ORDER BY realm_order")]
    assert values == sorted(values)
