"""Demo 5 - pytest-asyncio: kiểm thử hàm bất đồng bộ (async/await).

Đối tượng test: src/core/rate_limit.py::SlidingWindowRateLimiter (giới hạn tần suất theo cửa sổ trượt).
asyncio_mode = auto (xem pytest.ini) nên chỉ cần khai báo `async def test_...`.
"""
import pytest

from src.core.rate_limit import SlidingWindowRateLimiter


@pytest.mark.unit
async def test_cho_phep_den_gioi_han_roi_chan():
    rl = SlidingWindowRateLimiter()
    results = [await rl.allow("ip1", limit=3, window_seconds=60) for _ in range(4)]
    assert [ok for ok, _ in results] == [True, True, True, False]
    assert results[-1][1] >= 1          # có thời gian chờ retry-after


@pytest.mark.unit
async def test_moi_key_co_han_muc_rieng():
    rl = SlidingWindowRateLimiter()
    for _ in range(2):
        await rl.allow("a", limit=2, window_seconds=60)
    assert (await rl.allow("a", limit=2, window_seconds=60))[0] is False
    assert (await rl.allow("b", limit=2, window_seconds=60))[0] is True


@pytest.mark.unit
async def test_reset_xoa_lich_su():
    rl = SlidingWindowRateLimiter()
    await rl.allow("k", limit=1, window_seconds=60)
    assert (await rl.is_blocked("k", 1, 60))[0] is True
    await rl.reset("k")
    assert (await rl.is_blocked("k", 1, 60))[0] is False


@pytest.mark.unit
async def test_is_blocked_khong_tinh_them_luot():
    rl = SlidingWindowRateLimiter()
    for _ in range(5):
        await rl.is_blocked("k", 1, 60)
    assert (await rl.allow("k", limit=1, window_seconds=60))[0] is True
