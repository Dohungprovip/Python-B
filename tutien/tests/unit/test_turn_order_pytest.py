"""Demo 2 - pytest: hàm test thuần, assert trần, @pytest.mark.parametrize, pytest.raises.

Đối tượng test: src/core/turn_order.py (thứ tự lượt theo tốc độ trong chiến đấu).
"""
import pytest

from src.core.turn_order import MAX_ACTIONS, actions_for, build_round


@pytest.mark.unit
@pytest.mark.parametrize(
    "spd, opp, expected",
    [
        (1000, 1000, 1),   # ngang tốc độ -> 1 lượt
        (2000, 900, 2),    # >= 2 lần -> 2 lượt
        (3000, 1000, 3),
        (500, 1000, 1),    # chậm hơn vẫn tối thiểu 1 lượt
        (100, 0, 1),       # đối thủ SPD = 0 -> 1 lượt
        (10**6, 1, MAX_ACTIONS),  # bị chặn trần MAX_ACTIONS
    ],
)
def test_actions_for(spd, opp, expected):
    assert actions_for(spd, opp) == expected


@pytest.mark.unit
def test_build_round_nguoi_nhanh_hon_ra_don_truoc_va_xen_ke():
    actors = [{"k": "A", "spd": 2000}, {"k": "B", "spd": 900}]
    opp = {"A": 900, "B": 2000}
    order = [a["k"] for a in build_round(actors, opp)]
    assert order == ["A", "B", "A"]   # ví dụ trong docstring của module


@pytest.mark.unit
def test_build_round_cung_toc_do_dung_tie_de_phan_dinh():
    actors = [{"k": "X", "spd": 100, "tie": 2}, {"k": "Y", "spd": 100, "tie": 1}]
    order = [a["k"] for a in build_round(actors, {"X": 100, "Y": 100})]
    assert order == ["Y", "X"]


@pytest.mark.unit
def test_actions_for_loi_khi_toc_do_khong_phai_so():
    with pytest.raises((TypeError, ValueError)):
        actions_for("abc", 100)
