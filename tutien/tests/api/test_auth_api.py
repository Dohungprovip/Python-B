"""Demo 7 - Kiểm thử API với FastAPI TestClient (app thật, database tạm).

Luồng: đăng ký -> đăng nhập -> tạo nhân vật -> xem thông tin. Kèm các ca lỗi (409/401/422).
Lưu ý: app giới hạn 3 tài khoản mới / IP / giờ nên mỗi file chỉ đăng ký 1 tài khoản.
"""
import pytest

pytestmark = pytest.mark.api

USERNAME, PASSWORD = "tester_01", "matkhau123"


@pytest.fixture(scope="module")
def account(client):
    """Đăng ký 1 lần cho cả module, trả về token."""
    r = client.post("/api/register", json={"username": USERNAME, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_robots_txt(client):
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert "Disallow: /" in r.text


def test_chan_cong_cu_cao_du_lieu_theo_user_agent(client):
    """Lớp chống bot: UA của thư viện Python bị từ chối 403 dù endpoint hợp lệ."""
    r = client.post("/api/login", json={"username": "abc", "password": "abcd"},
                    headers={"user-agent": "python-requests/2.31"})
    assert r.status_code == 403


def test_trang_chu_tra_ve_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_dang_ky_thanh_cong_can_tao_nhan_vat(client, account):
    assert isinstance(account, str) and len(account) > 20
    me = client.get("/api/me", headers=auth(account))
    assert me.status_code == 200
    assert me.json() == {"needs_character_name": True}


def test_dang_ky_trung_ten_bi_tu_choi_409(client, account):
    r = client.post("/api/register", json={"username": USERNAME, "password": "khac1234"})
    assert r.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"username": "ab", "password": "abcd"},
        {"username": "co khoang trang", "password": "abcd"},
        {"username": "hople", "password": "123"},
        {"username": "hople"},
        {},
    ],
)
def test_dang_ky_du_lieu_sai_bi_tu_choi_422(client, payload):
    assert client.post("/api/register", json=payload).status_code == 422


def test_dang_nhap_sai_mat_khau_401(client, account):
    r = client.post("/api/login", json={"username": USERNAME, "password": "sai-mat-khau"})
    assert r.status_code == 401


def test_dang_nhap_tai_khoan_khong_ton_tai_401(client):
    assert client.post("/api/login", json={"username": "khongtontai", "password": "abcd1234"}).status_code == 401


def test_dang_nhap_dung_nhan_token_moi(client, account):
    r = client.post("/api/login", json={"username": USERNAME, "password": PASSWORD})
    assert r.status_code == 200
    body = r.json()
    assert body["token"] and body["token"] != account
    assert body["needs_character_name"] is True and body["player"] is None


def test_goi_api_khong_co_token_bi_tu_choi(client):
    assert client.get("/api/me").status_code in (401, 403)


def test_token_gia_bi_tu_choi(client):
    assert client.get("/api/me", headers=auth("token-gia")).status_code in (401, 403)


def test_tao_nhan_vat_roi_xem_thong_tin(client, account):
    r = client.post("/api/character/create", headers=auth(account), json={"ten": "Lăng Thiên", "gioi_tinh": 1})
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True

    me = client.get("/api/me", headers=auth(account)).json()
    assert me.get("needs_character_name") is not True
    assert "Lăng Thiên" in str(me)


def test_tao_nhan_vat_lan_hai_bi_tu_choi_409(client, account):
    r = client.post("/api/character/create", headers=auth(account), json={"ten": "Nhân Vật Hai", "gioi_tinh": 0})
    assert r.status_code == 409


def test_tao_nhan_vat_ten_khong_hop_le_422(client, account):
    r = client.post("/api/character/create", headers=auth(account), json={"ten": "A", "gioi_tinh": 0})
    assert r.status_code == 422
