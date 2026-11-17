import pytest

from src.features.skill_system import mo_ta
from src.features.than_hon import service as than_hon
from src.services import progression_balance_service as balance

pytestmark = pytest.mark.unit


class TestPct:
    @pytest.mark.parametrize(
        "value, text",
        [(0, "0"), (1, "100"), (0.5, "50"), (0.255, "25.5"), (1.66, "166"), (0.05, "5"), (0.125, "12.5")],
    )
    def test_dinh_dang_phan_tram(self, value, text):
        assert mo_ta.pct(value) == text

    def test_chap_nhan_chuoi_so(self):
        assert mo_ta.pct("0.2") == "20"


class TestEffectLine:
    def skill(self, kn, st="atk", coeff=1.5):
        return {"kha_nang": kn, "chi_so_su_dung": st, "thong_so": coeff}

    def test_sat_thuong(self):
        assert mo_ta.effect_line(self.skill(0)) == "Gây sát thương tương đương 150% Chiến lực"

    def test_sat_thuong_theo_chi_so_khac(self):
        assert "Phòng ngự" in mo_ta.effect_line(self.skill(0, "def"))

    def test_hoi_phuc(self):
        assert mo_ta.effect_line(self.skill(1, "hp", 0.2)) == "Hồi phục 20% Khí huyết tối đa"

    def test_tao_khien(self):
        assert "khiên" in mo_ta.effect_line(self.skill(2, "def", 0.3))

    def test_buff_bao_kich(self):
        assert mo_ta.effect_line(self.skill(3, "ti_le_bao_kich", 0.1)) == "Tăng Tỷ lệ bạo kích thêm 10% trong trận"

    def test_buff_tai_nguyen_bi_gioi_han_tran(self):
        text = mo_ta.effect_line(self.skill(3, "hp", 100.0))
        assert text.startswith("Hồi phục") and "Khí huyết" in text

    def test_buff_chi_so_khac_khong_cong_don(self):
        assert "không cộng dồn" in mo_ta.effect_line(self.skill(3, "atk", 0.2))

    def test_khong_che(self):
        assert mo_ta.effect_line(self.skill(4)) == "Khống chế đối thủ 1 lượt"

    @pytest.mark.parametrize("coeff, expected", [(0.01, "5"), (0.2, "20"), (0.9, "50")])
    def test_giam_chi_so_doi_thu_bi_ep_vao_5_den_50_phan_tram(self, coeff, expected):
        assert f"Giảm {expected}%" in mo_ta.effect_line(self.skill(5, "atk", coeff))

    def test_loai_khong_biet_tra_chuoi_rong(self):
        assert mo_ta.effect_line(self.skill(99)) == ""

    def test_thieu_chi_so_dung_mac_dinh_atk(self):
        assert "Chiến lực" in mo_ta.effect_line({"kha_nang": 0, "chi_so_su_dung": None, "thong_so": 1})


class TestEffectText:
    names = {"hoa_an": "Hỏa Ấn", "chay": "Cháy"}

    def eff(self, key, rate=0.5, turns=2):
        return {"hieu_ung_key": key, "ti_le": rate, "so_luot": turns}

    def test_thanh_tay(self):
        assert mo_ta.effect_text(self.eff("thanh_tay"), self.names) == "Xóa các hiệu ứng bất lợi trên bản thân"

    def test_pha_giai(self):
        assert "Xóa các hiệu ứng có lợi" in mo_ta.effect_text(self.eff("pha_giai"), self.names)

    def test_khieu_khich_hien_so_luot(self):
        assert "trong 3 lượt" in mo_ta.effect_text(self.eff("khieu_khich", turns=3), self.names)

    def test_hoa_an_dung_ten_hien_thi(self):
        text = mo_ta.effect_text(self.eff("hoa_an", 0.25), self.names)
        assert text.startswith("Có 25% gắn Hỏa Ấn lên đối thủ")


class TestBuildDesc:
    base = {"linh_can_can": "vo", "canh_gioi_yeu_cau": 2, "loai_kn": 0, "noinang": 120, "kha_nang": 0,
            "chi_so_su_dung": "atk", "thong_so": 1.0, "hoi_chieu": 3, "phan_loai": "chu_dong"}

    def test_mo_ta_ky_nang_chu_dong(self):
        text = mo_ta.build_desc(self.base, {2: "Khai Nguyên"}, [], {})
        lines = text.split("\n")
        assert "Cảnh giới học: Khai Nguyên" in lines
        assert "Nội năng tiêu hao: 120" in lines
        assert "Hồi chiêu: 3 lượt" in lines
        assert lines[-1] == "Loại kỹ năng: Chủ động"

    def test_ky_nang_bi_dong_tu_thi_trien(self):
        text = mo_ta.build_desc({**self.base, "loai_kn": 1}, {2: "Khai Nguyên"}, [], {})
        assert "Tự động thi triển khi hết hồi chiêu, không tốn Nội năng" in text

    def test_yeu_cau_linh_can(self):
        text = mo_ta.build_desc({**self.base, "linh_can_can": "kim-hoa"}, {2: "Khai Nguyên"}, [], {})
        assert text.split("\n")[0] == "Linh Căn cần: Kim Linh Căn hoặc Hỏa Linh Căn"

    def test_canh_gioi_khong_co_ten_thi_hien_so(self):
        assert "Cảnh giới học: 2" in mo_ta.build_desc(self.base, {}, [], {})

    def test_hieu_ung_phu_duoc_them_vao(self):
        text = mo_ta.build_desc(self.base, {2: "x"}, [{"hieu_ung_key": "thanh_tay", "ti_le": 1, "so_luot": 1}], {})
        assert "Xóa các hiệu ứng bất lợi trên bản thân" in text


class TestBalanceHelpers:
    @pytest.mark.parametrize("v, expected", [(0, 0), (-10, 0), (1, 1), (2, 1), (3, 2), (100, 50), (1001, 500)])
    def test_scale_exp_giam_mot_nua(self, v, expected):
        assert than_hon._scale_exp(v) == expected

    def test_scale_exp_khong_bao_gio_ve_0_khi_dau_vao_duong(self):
        assert all(than_hon._scale_exp(v) >= 1 for v in range(1, 50))

    def test_scale_exp_lam_tron_so_chan_cua_python(self):
        assert than_hon._scale_exp(5) == round(2.5) == 2

    @pytest.mark.parametrize("order, weight", [(1, 1.0), (8, 1.6), (15, 2.2)])
    def test_trong_so_canh_gioi(self, order, weight):
        assert balance._realm_weight(order) == pytest.approx(weight)

    @pytest.mark.parametrize("order, clamped", [(0, 1), (-3, 1), (99, 15)])
    def test_trong_so_bi_ep_vao_khoang_1_den_15(self, order, clamped):
        assert balance._realm_weight(order) == balance._realm_weight(clamped)

    def test_trong_so_tang_dan(self):
        weights = [balance._realm_weight(i) for i in range(1, 16)]
        assert weights == sorted(weights) and len(set(weights)) == 15

    def test_muc_tieu_chi_so_lon_hon_co_so(self):
        assert balance.TARGET_HP > balance.BASE_HP
        assert balance.TARGET_ATK > balance.BASE_ATK
        assert balance.TARGET_DEF > balance.BASE_DEF
        assert balance.TARGET_NN > balance.BASE_NN

    def test_ty_le_hp_atk_def_muc_tieu_giu_cau_truc_game(self):
        assert balance.TARGET_HP / balance.TARGET_ATK == 10
        assert balance.TARGET_DEF / balance.TARGET_ATK == pytest.approx(0.7)
