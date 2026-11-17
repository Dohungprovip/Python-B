"""Demo 6 - Mock: cô lập phụ thuộc bên ngoài bằng unittest.mock / pytest-mock.

Ba kỹ thuật:
  1. patch thời gian (time.monotonic) để test cửa sổ trượt mà không phải chờ.
  2. patch random để kết quả "ngẫu nhiên" trở nên xác định.
  3. AsyncMock giả lập đối tượng database (không cần DB thật), kiểm tra lời gọi bằng assert_awaited_*.

Đối tượng test: src/core/rate_limit.py, src/services/linh_can_service.py.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.rate_limit import SlidingWindowRateLimiter
from src.services import linh_can_service as lc


# ---------- 1. Giả lập thời gian ----------
@pytest.mark.unit
async def test_cua_so_truot_het_han_khi_thoi_gian_troi_qua():
    rl = SlidingWindowRateLimiter()
    with patch("src.core.rate_limit.time.monotonic") as fake_time:
        fake_time.return_value = 1000.0
        assert (await rl.allow("ip", 1, 10))[0] is True
        fake_time.return_value = 1005.0            # còn trong cửa sổ 10s
        ok, retry = await rl.allow("ip", 1, 10)
        assert ok is False and retry == 5
        fake_time.return_value = 1011.0            # đã ra khỏi cửa sổ
        assert (await rl.allow("ip", 1, 10))[0] is True


# ---------- 2. Giả lập random + 3. Giả lập DB ----------
def make_db(drop_pct=0.2):
    db = MagicMock()
    db.get_cau_hinh_float = AsyncMock(return_value=drop_pct)
    db.them_vat_pham = AsyncMock()
    return db


@pytest.mark.unit
async def test_roll_drop_trung_thuong_them_vat_pham_vao_kho(mocker):
    db = make_db(drop_pct=0.2)
    mocker.patch.object(lc.random, "random", return_value=0.0)       # luôn trúng
    mocker.patch.object(lc.random, "choice", return_value="hoa")     # luôn ra hệ Hỏa
    boss = {"type": 2, "canh_gioi": 10}                              # Thủ Lĩnh, cảnh giới 10 -> Thượng phẩm

    result = await lc.roll_drop(db, 42, boss)

    expected_id = lc.item_id("hoa", "thuong")
    db.them_vat_pham.assert_awaited_once_with(42, expected_id, 1)
    assert result == [{"id": expected_id, "ten": "Linh Căn Tinh Hỏa · Thượng phẩm", "so_luong": 1}]


@pytest.mark.unit
async def test_roll_drop_khong_trung_thi_khong_goi_db(mocker):
    db = make_db(drop_pct=0.2)
    mocker.patch.object(lc.random, "random", return_value=0.99)      # 99% >= 0.2% -> trượt
    assert await lc.roll_drop(db, 1, {"type": 2, "canh_gioi": 3}) == []
    db.them_vat_pham.assert_not_awaited()


@pytest.mark.unit
async def test_roll_drop_quai_thuong_khong_rot():
    db = make_db()
    assert await lc.roll_drop(db, 1, {"type": 0, "canh_gioi": 3}) == []
    db.get_cau_hinh_float.assert_not_awaited()     # thoát sớm, chưa đọc cấu hình


@pytest.mark.unit
async def test_roll_drop_loi_db_duoc_nuot_va_tra_danh_sach_rong(mocker):
    db = make_db()
    db.them_vat_pham.side_effect = RuntimeError("DB hỏng")           # giả lập lỗi
    mocker.patch.object(lc.random, "random", return_value=0.0)
    assert await lc.roll_drop(db, 1, {"type": 2, "canh_gioi": 1}) == []


# ---------- Hàm thuần của cùng module ----------
@pytest.mark.unit
@pytest.mark.parametrize(
    "realm, tier",
    [(1, "ha"), (4, "ha"), (5, "trung"), (8, "trung"), (9, "thuong"), (12, "thuong"), (13, "cuc"), (15, "cuc"), (None, "ha")],
)
def test_tier_for_realm(realm, tier):
    assert lc.tier_for_realm(realm) == tier


@pytest.mark.unit
def test_item_id_la_duy_nhat_cho_20_to_hop():
    ids = {lc.item_id(he, t) for he in lc.ELEMENTS for t in lc.TIERS}
    assert len(ids) == 20 and min(ids) == 980001 and max(ids) == 980020


@pytest.mark.unit
def test_vn_dinh_dang_so_kieu_viet():
    assert lc._vn(20000) == "20.000"
    assert lc._vn(1500000) == "1.500.000"
