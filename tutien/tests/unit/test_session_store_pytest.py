"""Demo 3 - pytest nâng cao: fixture, tham số hoá, kiểm tra TTL bằng đồng hồ giả.

Đối tượng test: src/core/session_store.py::ExpiringSessionStore (phiên đăng nhập có hạn).
"""
import pytest

from src.core.session_store import ExpiringSessionStore


class FakeClock:
    """Đồng hồ giả: test điều khiển được thời gian, không cần time.sleep."""

    def __init__(self, now=1_000_000):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def store(clock):
    return ExpiringSessionStore(ttl_seconds=120, max_entries=100, clock=clock)


@pytest.mark.unit
def test_luu_va_lay_phien(store):
    store["tok1"] = {"user_id": 7, "name": "alice"}
    s = store.get("tok1")
    assert s["user_id"] == 7
    assert {"created_at", "last_seen", "expires_at"} <= s.keys()


@pytest.mark.unit
def test_token_khong_ton_tai_tra_ve_default(store):
    assert store.get("khong-co") is None
    assert store.get("khong-co", "mac-dinh") == "mac-dinh"


@pytest.mark.unit
def test_phien_het_han_bi_xoa(store, clock):
    store["tok"] = {"user_id": 1}
    clock.advance(121)                 # quá TTL 120 giây
    assert store.get("tok") is None
    assert "tok" not in store


@pytest.mark.unit
def test_truy_cap_gia_han_phien(store, clock):
    store["tok"] = {"user_id": 1}
    clock.advance(100)
    assert store.get("tok") is not None    # touch -> gia hạn thêm 120s
    clock.advance(100)
    assert store.get("tok") is not None    # nếu không gia hạn thì đã hết hạn (200 > 120)


@pytest.mark.unit
def test_peek_khong_gia_han(store, clock):
    store["tok"] = {"user_id": 1}
    clock.advance(100)
    assert store.peek("tok") is not None
    clock.advance(30)                      # tổng 130 > 120, peek không gia hạn
    assert store.get("tok") is None


@pytest.mark.unit
def test_revoke_user_thu_hoi_moi_phien_cua_user(store):
    store["a"] = {"user_id": 5}
    store["b"] = {"user_id": 5}
    store["c"] = {"user_id": 6}
    assert store.revoke_user(5) == 2
    assert len(store) == 1 and "c" in store


@pytest.mark.unit
def test_gioi_han_so_phien_loai_phien_cu_nhat(clock):
    store = ExpiringSessionStore(ttl_seconds=3600, max_entries=100, clock=clock)  # min là 100
    for i in range(105):
        clock.advance(1)
        store[f"t{i}"] = {"user_id": i}
    assert len(store) == 100
    assert "t0" not in store and "t104" in store


@pytest.mark.unit
@pytest.mark.parametrize("ttl, expected", [(1, 60), (0, 60), (600, 600)])
def test_ttl_toi_thieu_60_giay(ttl, expected):
    assert ExpiringSessionStore(ttl_seconds=ttl).ttl_seconds == expected
