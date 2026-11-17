import pytest

from src.features.thien_phu import skills as S

pytestmark = pytest.mark.unit


@pytest.fixture
def fixed_random(monkeypatch):
    def set_value(value):
        monkeypatch.setattr(S.random, "random", lambda: value)

    return set_value


@pytest.fixture
def log():
    return []


class TestTurnTick:
    def test_giam_bo_dem_mien_choang_va_ma_the(self, log):
        state = {"stun_immune": 2, "mt_turns": 3}
        S.turn_tick({}, state, 500, 1000, log)
        assert state == {"stun_immune": 1, "mt_turns": 2}

    def test_ma_the_kich_hoat_khi_mau_duoi_nguong(self, log):
        state = {}
        hp, burn = S.turn_tick({"ma_the": 1.0}, state, 300, 1000, log)
        assert state["mt_used"] == 1 and state["mt_turns"] == S.MA_THE_TURNS
        assert (hp, burn) == (300, 0)
        assert len(log) == 1

    def test_ma_the_khong_kich_hoat_khi_tren_nguong(self, log):
        state = {}
        S.turn_tick({"ma_the": 1.0}, state, 301, 1000, log)
        assert "mt_used" not in state and log == []

    def test_ma_the_chi_kich_hoat_mot_lan(self, log):
        state = {"mt_used": 1}
        S.turn_tick({"ma_the": 1.0}, state, 100, 1000, log)
        assert state.get("mt_turns", 0) == 0

    def test_ma_the_khong_kich_hoat_khi_da_chet(self, log):
        state = {}
        S.turn_tick({"ma_the": 1.0}, state, 0, 1000, log)
        assert "mt_used" not in state

    @pytest.mark.parametrize("s, heal", [(1.0, 20), (0.5, 10), (0.25, 5)])
    def test_tu_quang_hoi_theo_suc_manh(self, log, s, heal):
        hp, _ = S.turn_tick({"tu_quang": s}, {}, 500, 1000, log)
        assert hp == 500 + heal

    def test_tu_quang_khong_hoi_khi_day_mau(self, log):
        hp, _ = S.turn_tick({"tu_quang": 1.0}, {}, 1000, 1000, log)
        assert hp == 1000 and log == []

    def test_hoi_phuc_khong_vuot_hp_toi_da(self, log):
        hp, _ = S.turn_tick({"tu_quang": 1.0}, {}, 995, 1000, log)
        assert hp == 1000

    def test_nguoi_da_chet_khong_duoc_hoi(self, log):
        hp, _ = S.turn_tick({"tu_quang": 1.0, "thanh_khu": 1.0}, {}, 0, 1000, log)
        assert hp == 0

    def test_thanh_khu_hoi_hai_phan_tram(self, log):
        hp, _ = S.turn_tick({"thanh_khu": 1.0}, {}, 500, 1000, log)
        assert hp == 520

    def test_hai_noi_tai_hoi_cong_don(self, log):
        hp, _ = S.turn_tick({"tu_quang": 1.0, "thanh_khu": 1.0}, {}, 500, 1000, log)
        assert hp == 540

    @pytest.mark.parametrize("he", list(S.NGU_HANH))
    def test_ngu_hanh_moi_luot_chon_mot_he(self, monkeypatch, log, he):
        monkeypatch.setattr(S.random, "choice", lambda seq: he)
        state = {}
        hp, _ = S.turn_tick({"ngu_hanh": 1.0}, state, 500, 1000, log)
        assert state["nh"] == he
        assert hp == (540 if he == "moc" else 500)

    def test_kim_than_hoi_nam_phan_tram_va_giam_luot(self, log):
        state = {"kt_turns": 2}
        hp, _ = S.turn_tick({}, state, 500, 1000, log)
        assert hp == 550 and state["kt_turns"] == 1

    def test_dot_hon_tra_sat_thuong_va_giam_luot(self, log):
        state = {"burn_turns": 2, "burn_dmg": 77}
        hp, burn = S.turn_tick({}, state, 500, 1000, log)
        assert burn == 77 and state["burn_turns"] == 1

    def test_het_dot_hon_khong_gay_sat_thuong(self, log):
        _, burn = S.turn_tick({}, {"burn_turns": 0, "burn_dmg": 99}, 500, 1000, log)
        assert burn == 0

    def test_burn_dmg_am_duoc_coi_la_khong(self, log):
        _, burn = S.turn_tick({}, {"burn_turns": 1, "burn_dmg": -5}, 500, 1000, log)
        assert burn == 0


class TestReduceIncoming:
    def test_khong_noi_tai_thi_giu_nguyen(self, log):
        assert S.reduce_incoming({}, {}, 1000, log) == (1000, 0)

    def test_bat_khuat_nuot_tron_don_va_tieu_hao_khien(self, log):
        tps = {"bk_shield": 1}
        assert S.reduce_incoming({}, tps, 1000, log) == (0, 0)
        assert tps["bk_shield"] == 0

    def test_phan_chan_chan_hoan_toan(self, fixed_random, log):
        fixed_random(0.0)
        assert S.reduce_incoming({"phan_chan": 1.0}, {}, 1000, log) == (0, 0)

    def test_phan_chan_khong_chan_thi_phan_don(self, fixed_random, log):
        fixed_random(0.99)
        assert S.reduce_incoming({"phan_chan": 1.0}, {}, 1000, log) == (1000, 120)

    def test_thanh_khu_giam_15_phan_tram(self, log):
        assert S.reduce_incoming({"thanh_khu": 1.0}, {}, 1000, log)[0] == 850

    def test_thanh_khu_cong_vo_cuc_giam_25_phan_tram(self, log):
        assert S.reduce_incoming({"thanh_khu": 1.0, "vo_cuc": 1.0}, {}, 1000, log)[0] == 750

    @pytest.mark.parametrize("he, expected", [("thuy", 850), ("tho", 750), ("kim", 1000), ("hoa", 1000), ("moc", 1000)])
    def test_ngu_hanh_giam_sat_thuong_theo_he(self, log, he, expected):
        assert S.reduce_incoming({"ngu_hanh": 1.0}, {"nh": he}, 1000, log)[0] == expected

    def test_sat_thuong_toi_thieu_la_1(self, log):
        assert S.reduce_incoming({"thanh_khu": 1.0}, {}, 1, log)[0] == 1

    def test_kim_than_giam_mot_nua(self, log):
        assert S.reduce_incoming({}, {"kt_turns": 1}, 1000, log)[0] == 500

    def test_ma_the_nhan_them_20_phan_tram(self, log):
        assert S.reduce_incoming({}, {"mt_turns": 1}, 1000, log)[0] == 1200

    def test_the_than_can_co_linh_thu(self, fixed_random, log):
        fixed_random(0.0)
        assert S.reduce_incoming({"the_than": 1.0}, {}, 1000, log, has_pet=False)[0] == 1000
        assert S.reduce_incoming({"the_than": 1.0}, {}, 1000, log, has_pet=True)[0] == 500

    def test_the_phach_tich_tang_va_giam_sat_thuong(self, log):
        tps = {"tp_stacks": 4}
        dmg, _ = S.reduce_incoming({"the_phach": 1.0}, tps, 1000, log)
        assert dmg == 940 and tps["tp_stacks"] == 5

    def test_the_phach_toi_da_10_tang(self, log):
        tps = {"tp_stacks": S.THE_PHACH_MAX_STACKS}
        S.reduce_incoming({"the_phach": 1.0}, tps, 1000, log)
        assert tps["tp_stacks"] == S.THE_PHACH_MAX_STACKS

    def test_the_phach_lan_dau_chua_giam(self, log):
        tps = {}
        assert S.reduce_incoming({"the_phach": 1.0}, tps, 1000, log)[0] == 1000
        assert tps["tp_stacks"] == 1


class TestSecondWindAndAfterHit:
    def test_bat_khuat_hoi_sinh_30_phan_tram(self, log):
        tps = {}
        assert S.second_wind({"bat_khuat": 1.0}, tps, 0, 1000, log) == 300
        assert tps["bk_used"] == 1 and tps["bk_shield"] == 1

    def test_bat_khuat_theo_suc_manh(self, log):
        assert S.second_wind({"bat_khuat": 0.5}, {}, 0, 1000, log) == 150

    def test_bat_khuat_chi_mot_lan_moi_tran(self, log):
        assert S.second_wind({"bat_khuat": 1.0}, {"bk_used": 1}, 0, 1000, log) == 0

    def test_con_song_thi_khong_kich_hoat(self, log):
        assert S.second_wind({"bat_khuat": 1.0}, {}, 50, 1000, log) == 50

    def test_khong_co_ky_nang_thi_van_chet(self, log):
        assert S.second_wind({}, {}, 0, 1000, log) == 0

    def test_hoi_sinh_toi_thieu_1_hp(self, log):
        assert S.second_wind({"bat_khuat": 0.01}, {}, 0, 10, log) == 1

    @pytest.mark.parametrize("php, kich_hoat", [(400, True), (1, True), (401, False), (0, False)])
    def test_kim_than_kich_hoat_o_nguong_40_phan_tram(self, log, php, kich_hoat):
        tps = {}
        S.after_hit({"kim_than": 1.0}, tps, php, 1000, log)
        assert bool(tps.get("kt_used")) is kich_hoat
        if kich_hoat:
            assert tps["kt_turns"] == S.KIM_THAN_TURNS

    def test_kim_than_chi_kich_hoat_mot_lan(self, log):
        tps = {"kt_used": 1}
        S.after_hit({"kim_than": 1.0}, tps, 100, 1000, log)
        assert "kt_turns" not in tps


class TestOutgoing:
    def test_he_so_co_ban_la_1(self):
        assert S.out_damage_mult({}, {}, 500, 1000) == 1.0

    @pytest.mark.parametrize("hp, expected", [(0, 1.4), (500, 1.2), (1000, 1.0), (-50, 1.4), (5000, 1.0)])
    def test_khat_mau_tang_theo_mau_da_mat(self, hp, expected):
        assert S.out_damage_mult({"khat_mau": 1.0}, {}, hp, 1000) == pytest.approx(expected)

    def test_khat_mau_theo_suc_manh(self):
        assert S.out_damage_mult({"khat_mau": 0.5}, {}, 0, 1000) == pytest.approx(1.2)

    def test_hp_toi_da_bang_khong_khong_chia_cho_0(self):
        assert S.out_damage_mult({"khat_mau": 1.0}, {}, 0, 0) == 1.0

    def test_ma_the_dang_chay_cong_50_phan_tram(self):
        assert S.out_damage_mult({}, {"mt_turns": 2}, 500, 1000) == pytest.approx(1.5)

    def test_vo_cuc_cong_10_phan_tram(self):
        assert S.out_damage_mult({"vo_cuc": 1.0}, {}, 500, 1000) == pytest.approx(1.1)

    @pytest.mark.parametrize("he, expected", [("kim", 1.2), ("hoa", 1.12), ("thuy", 1.0), ("", 1.0)])
    def test_ngu_hanh_tang_sat_thuong(self, he, expected):
        assert S.out_damage_mult({"ngu_hanh": 1.0}, {"nh": he}, 500, 1000) == pytest.approx(expected)

    @pytest.mark.parametrize(
        "state, expected",
        [({}, 0.0), ({"mt_turns": 1}, 25.0), ({"nh": "hoa"}, 8.0), ({"mt_turns": 1, "nh": "hoa"}, 33.0), ({"nh": "kim"}, 0.0)],
    )
    def test_hut_mau(self, state, expected):
        assert S.out_lifesteal(state) == expected

    @pytest.mark.parametrize(
        "sk, crit, expected",
        [
            ({}, True, 1000),
            ({"pha_giap": 1.0}, True, 750),
            ({"pha_giap": 1.0}, False, 1000),
            ({"pha_giap": 0.5}, True, 875),
            ({"phe_thien": 1.0}, False, 800),
            ({"pha_giap": 1.0, "phe_thien": 1.0}, True, 600),
        ],
    )
    def test_bo_qua_phong_thu(self, sk, crit, expected):
        assert S.ignore_defense(sk, 1000, crit) == expected

    def test_hut_mau_tu_don_bao_kich(self):
        hits = [(100, True), (200, False), (300, True)]
        assert S.crit_lifesteal({"phe_thien": 1.0}, hits) == 60
        assert S.crit_lifesteal({}, hits) == 0

    def test_khong_co_don_bao_kich_khong_hut_mau(self):
        assert S.crit_lifesteal({"phe_thien": 1.0}, [(100, False)]) == 0

    def test_vo_cuc_tung_them_mot_nhat(self, fixed_random, log):
        fixed_random(0.0)
        assert S.extra_strike({"vo_cuc": 1.0}, 1000, log) == 600
        assert len(log) == 1

    def test_vo_cuc_khong_may_man_thi_khong_them(self, fixed_random, log):
        fixed_random(0.5)
        assert S.extra_strike({"vo_cuc": 1.0}, 1000, log) == 0 and log == []

    def test_nhat_them_toi_thieu_1(self, fixed_random, log):
        fixed_random(0.0)
        assert S.extra_strike({"vo_cuc": 1.0}, 1, log) == 1

    def test_khong_co_vo_cuc_thi_khong_them(self, fixed_random, log):
        fixed_random(0.0)
        assert S.extra_strike({}, 1000, log) == 0

    def test_he_so_ky_nang_chu_dong(self):
        assert S.skill_damage_mult({}) == 1.0
        assert S.skill_damage_mult({"dao_van": 1.0}) == pytest.approx(1.3)
        assert S.skill_lifesteal({"dao_van": 1.0}) == 10.0
        assert S.skill_lifesteal({}) == 0.0


class TestWuxingGuard:
    @pytest.mark.parametrize(
        "atk, dfn, mult, expected",
        [
            ({}, {}, 0.8, 0.8),
            ({}, {}, 1.2, 1.2),
            ({"ngu_hanh": 1}, {}, 0.8, 1.0),
            ({"ngu_hanh": 1}, {}, 1.2, 1.2),
            ({}, {"ngu_hanh": 1}, 1.2, 1.0),
            ({}, {"ngu_hanh": 1}, 0.8, 0.8),
            ({"ngu_hanh": 1}, {"ngu_hanh": 1}, 0.8, 1.0),
            ({"ngu_hanh": 1}, {"ngu_hanh": 1}, 1.2, 1.0),
        ],
    )
    def test_khong_bi_khac_che(self, atk, dfn, mult, expected):
        assert S.wuxing_guard(atk, dfn, mult) == pytest.approx(expected)


class TestOutgoingBonus:
    def test_khong_noi_tai_khong_cong_them(self, log):
        assert S.outgoing_bonus({}, {}, [(1000, True)], False, 5000, 5000, False, log) == 0

    def test_kiem_y_bao_phat_dung_mot_nua_don_dau(self, log):
        tps = {"ky_stacks": 5}
        extra = S.outgoing_bonus({"kiem_y": 1.0}, tps, [(1000, False)], True, 5000, 5000, False, log)
        assert extra == 500 and tps["ky_stacks"] == 0

    def test_kiem_y_tich_tang_theo_don_bao_kich(self, log):
        tps = {"ky_stacks": 3}
        S.outgoing_bonus({"kiem_y": 1.0}, tps, [(10, True), (10, True), (10, True)], False, 5000, 5000, False, log)
        assert tps["ky_stacks"] == S.KIEM_Y_STACKS

    def test_kiem_y_khong_tang_khi_khong_bao_kich(self, log):
        tps = {}
        S.outgoing_bonus({"kiem_y": 1.0}, tps, [(10, False)], False, 5000, 5000, False, log)
        assert tps.get("ky_stacks", 0) == 0

    def test_kiem_y_san_sang_khi_du_tang(self):
        assert S.kiem_y_ready({"kiem_y": 1}, {"ky_stacks": 5}) is True
        assert S.kiem_y_ready({"kiem_y": 1}, {"ky_stacks": 4}) is False
        assert S.kiem_y_ready({}, {"ky_stacks": 5}) is False

    def test_ket_lieu_boss_cong_30_phan_tram(self, log):
        assert S.outgoing_bonus({"ket_lieu": 1.0}, {}, [(1000, False)], False, 100000, 100000, True, log) == 300

    def test_ket_lieu_cham_chet_quai_sap_het_mau(self, log):
        extra = S.outgoing_bonus({"ket_lieu": 1.0}, {}, [(1000, False)], False, 1100, 1000, False, log)
        assert extra == 100

    def test_ket_lieu_khong_chem_khi_con_nhieu_mau(self, log):
        assert S.outgoing_bonus({"ket_lieu": 1.0}, {}, [(1000, False)], False, 1200, 1000, False, log) == 0

    def test_ket_lieu_khong_chem_quai_da_chet(self, log):
        assert S.outgoing_bonus({"ket_lieu": 1.0}, {}, [(1000, False)], False, 900, 1000, False, log) == 0

    def test_ket_lieu_pvp_chi_them_sat_thuong_khi_doi_thu_yeu(self, log):
        low = S.outgoing_bonus({"ket_lieu": 1.0}, {}, [(1000, False)], False, 300, 1000, False, log, pvp=True)
        high = S.outgoing_bonus({"ket_lieu": 1.0}, {}, [(1000, False)], False, 301, 1000, False, log, pvp=True)
        assert (low, high) == (300, 0)


class TestRandomSkills:
    def test_dot_hon_chay_khi_trung(self, fixed_random, log):
        fixed_random(0.0)
        state = {}
        S.apply_burn({"ma_tam": 1.0}, state, 1000, log)
        assert state == {"burn_turns": S.BURN_TURNS, "burn_dmg": 200}

    @pytest.mark.parametrize("value, dealt, sk", [(0.99, 1000, {"ma_tam": 1.0}), (0.0, 0, {"ma_tam": 1.0}), (0.0, 1000, {})])
    def test_dot_hon_khong_chay(self, fixed_random, log, value, dealt, sk):
        fixed_random(value)
        state = {}
        S.apply_burn(sk, state, dealt, log)
        assert state == {}

    def test_dot_hon_toi_thieu_1_sat_thuong(self, fixed_random, log):
        fixed_random(0.0)
        state = {}
        S.apply_burn({"ma_tam": 1.0}, state, 1, log)
        assert state["burn_dmg"] == 1

    def test_choang_pve(self, fixed_random):
        fixed_random(0.05)
        assert S.roll_stun({"do_hoa": 1.0}, pvp=False) is True
        fixed_random(0.5)
        assert S.roll_stun({"do_hoa": 1.0}, pvp=False) is False

    def test_choang_pvp_nguong_thap_hon(self, fixed_random):
        fixed_random(0.07)
        assert S.roll_stun({"do_hoa": 1.0}, pvp=False, target_state={}) is True
        assert S.roll_stun({"do_hoa": 1.0}, pvp=True, target_state={}) is False

    def test_choang_pvp_dat_mien_choang_cho_doi_thu(self, fixed_random):
        fixed_random(0.0)
        target = {}
        assert S.roll_stun({"do_hoa": 1.0}, pvp=True, target_state=target) is True
        assert target["stun_immune"] == 1
        assert S.roll_stun({"do_hoa": 1.0}, pvp=True, target_state=target) is False

    def test_khong_co_do_hoa_khong_choang(self, fixed_random):
        fixed_random(0.0)
        assert S.roll_stun({}, pvp=False) is False

    @pytest.mark.parametrize("value, chance, s, expected", [(0.1, 0.5, 1.0, True), (0.6, 0.5, 1.0, False), (0.2, 0.5, 0.5, True), (0.3, 0.5, 0.5, False)])
    def test_roll_ket_hop_suc_manh(self, fixed_random, value, chance, s, expected):
        fixed_random(value)
        assert S.roll({"x": s}, "x", chance) is expected

    def test_roll_khong_co_ky_nang(self, fixed_random):
        fixed_random(0.0)
        assert S.roll({}, "x", 1.0) is False


class TestPets:
    def test_so_linh_thu_duoc_deo(self):
        assert S.allowed_pets({}) == 1
        assert S.allowed_pets({"song_thu": 1.0}) == 2

    @pytest.mark.parametrize("name", S.PET_SKILLS)
    def test_pvp_pet_bat_khi_co_ky_nang_thu_dao(self, name):
        assert S.pvp_pet_enabled({name: 1.0}) is True

    def test_pvp_pet_tat_khi_khong_co(self):
        assert S.pvp_pet_enabled({"kim_than": 1.0}) is False


class TestAlchemyRefund:
    def test_hoan_mot_nua_vao_o_da_co(self):
        new_inv = [{"vp_key": "linh_thao", "so_luong": 3}]
        names = S.alchemy_refund({"giu_lua": 1}, [{"vp_key": "linh_thao", "so_luong": 4, "ten": "Linh Thảo"}], [], new_inv)
        assert new_inv[0]["so_luong"] == 5 and names == ["Linh Thảo"]

    def test_tao_o_moi_khi_da_het_trong_kho(self):
        current = [{"vp_key": "linh_thao", "so_luong": 10, "ten": "Linh Thảo"}]
        new_inv = []
        S.alchemy_refund({}, [{"vp_key": "linh_thao", "so_luong": 6}], current, new_inv)
        assert new_inv == [{"vp_key": "linh_thao", "so_luong": 3, "ten": "Linh Thảo"}]
        assert current[0]["so_luong"] == 10

    def test_so_luong_le_lam_tron_xuong_va_bo_qua_khi_bang_0(self):
        new_inv = []
        names = S.alchemy_refund({}, [{"vp_key": "a", "so_luong": 1}], [{"vp_key": "a"}], new_inv)
        assert names == [] and new_inv == []

    def test_khong_tim_thay_vat_pham_goc_thi_bo_qua(self):
        new_inv = []
        assert S.alchemy_refund({}, [{"vp_key": "x", "so_luong": 10}], [], new_inv) == []
        assert new_inv == []


class TestConstants:
    @pytest.mark.parametrize(
        "name",
        [n for n in dir(S) if n.isupper() and isinstance(getattr(S, n), float) and getattr(S, n) <= 1.0],
    )
    def test_ti_le_nam_trong_khoang_0_den_1(self, name):
        assert 0.0 <= getattr(S, name) <= 1.0

    def test_moi_the_chat_thuong_pham_co_noi_tai_rieng(self):
        skills = [v["skill"] for v in S.THE_CHAT_SKILLS.values()]
        assert len(skills) == len(set(skills)) == 5
        assert all(v["name"] and v["desc"] for v in S.THE_CHAT_SKILLS.values())

    def test_ngu_hanh_du_nam_he(self):
        assert set(S.NGU_HANH) == {"kim", "moc", "thuy", "hoa", "tho"}
