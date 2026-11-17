"""Demo 4 - pytest + pydantic: kiểm thử dữ liệu đầu vào (validation) của API.

Đối tượng test: src/api/schemas.py (AuthBody, CharacterCreateBody, ChangePasswordBody).
"""
import pytest
from pydantic import ValidationError

from src.api.schemas import AuthBody, ChangePasswordBody, CharacterCreateBody


@pytest.mark.unit
def test_auth_body_hop_le():
    b = AuthBody(username="user_01-ok", password="abcd")
    assert b.username == "user_01-ok"


@pytest.mark.unit
@pytest.mark.parametrize(
    "username, password",
    [
        ("ab", "abcd"),            # username < 3 ký tự
        ("a" * 21, "abcd"),        # username > 20 ký tự
        ("user name", "abcd"),     # có khoảng trắng
        ("user@name", "abcd"),     # ký tự đặc biệt
        ("tiếng_việt", "abcd"),    # dấu tiếng Việt không hợp lệ
        ("validuser", "abc"),      # password < 4 ký tự
        ("validuser", "x" * 65),   # password > 64 ký tự
    ],
)
def test_auth_body_khong_hop_le(username, password):
    with pytest.raises(ValidationError):
        AuthBody(username=username, password=password)


@pytest.mark.unit
@pytest.mark.parametrize("gioi_tinh", [0, 1])
def test_character_create_hop_le(gioi_tinh):
    assert CharacterCreateBody(ten="Lăng Thiên", gioi_tinh=gioi_tinh).gioi_tinh == gioi_tinh


@pytest.mark.unit
@pytest.mark.parametrize("ten, gioi_tinh", [("A", 0), ("x" * 25, 0), ("Hợp lệ", 2), ("Hợp lệ", -1)])
def test_character_create_khong_hop_le(ten, gioi_tinh):
    with pytest.raises(ValidationError):
        CharacterCreateBody(ten=ten, gioi_tinh=gioi_tinh)


@pytest.mark.unit
def test_change_password_thieu_truong():
    with pytest.raises(ValidationError) as exc:
        ChangePasswordBody(current_password="abcd")
    assert "new_password" in str(exc.value)
