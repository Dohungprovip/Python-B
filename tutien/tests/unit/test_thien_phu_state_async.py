from types import SimpleNamespace
from unittest.mock import AsyncMock

import aiosqlite
import pytest

from src.features.thien_phu import skills as S

pytestmark = pytest.mark.unit


@pytest.fixture
async def db():
    conn = await aiosqlite.connect(":memory:")
    conn.row_factory = aiosqlite.Row
    await conn.execute("CREATE TABLE nguoi_choi (user_id INTEGER PRIMARY KEY, tp_trang_thai TEXT)")
    await conn.execute("CREATE TABLE quai (id INTEGER PRIMARY KEY, type INTEGER)")
    await conn.executemany("INSERT INTO nguoi_choi VALUES (?, ?)", [(1, "{}"), (2, None), (3, "khong phai json"), (4, "[1, 2]")])
    await conn.executemany("INSERT INTO quai VALUES (?, ?)", [(10, 0), (11, 1), (12, 2), (13, None)])
    await conn.commit()
    yield SimpleNamespace(_conn=conn)
    await conn.close()


async def test_luu_roi_nap_lai_trang_thai(db):
    await S.save_state(db, 1, {"tp_stacks": 3, "bk_used": 1})
    assert await S.load_state(db, 1) == {"tp_stacks": 3, "bk_used": 1}


async def test_nap_trang_thai_null_tra_ve_rong(db):
    assert await S.load_state(db, 2) == {}


@pytest.mark.parametrize("user_id", [3, 4, 999])
async def test_du_lieu_hong_hoac_khong_phai_dict_tra_ve_rong(db, user_id):
    assert await S.load_state(db, user_id) == {}


async def test_luu_khong_commit_van_doc_lai_duoc_trong_cung_ket_noi(db):
    await S.save_state(db, 1, {"x": 1}, commit=False)
    assert await S.load_state(db, 1) == {"x": 1}


async def test_xoa_trang_thai_nhieu_nguoi_choi(db):
    await S.save_state(db, 1, {"a": 1})
    await S.save_state(db, 2, {"b": 2})
    await S.clear_state(db, 1, 2)
    assert await S.load_state(db, 1) == {}
    assert await S.load_state(db, 2) == {}


async def test_xoa_trang_thai_khi_chua_co_cot_khong_nem_loi():
    conn = await aiosqlite.connect(":memory:")
    await conn.execute("CREATE TABLE nguoi_choi (user_id INTEGER PRIMARY KEY)")
    await S.clear_state(SimpleNamespace(_conn=conn), 1)
    await conn.close()


@pytest.mark.parametrize("quai_id, is_boss", [(10, False), (11, False), (12, True), (13, False), (999, False), (0, False), (None, False)])
async def test_nhan_biet_boss_theo_loai_quai(db, quai_id, is_boss):
    assert await S.monster_is_boss(db, {"quai_id": quai_id}) is is_boss


async def test_trang_thai_quai_thieu_khoa_coi_nhu_khong_phai_boss(db):
    assert await S.monster_is_boss(db, {}) is False


async def test_combat_skills_gop_ky_nang_thien_phu_va_the_chat(monkeypatch, db):
    from src.features.the_chat import service as the_chat
    from src.features.thien_phu import service as thien_phu

    monkeypatch.setattr(thien_phu, "get_thien_phu_skills", AsyncMock(return_value={"kim_than": 0.5}))
    monkeypatch.setattr(the_chat, "get_the_chat_row", AsyncMock(return_value={"key": "hoang_co_thanh_the"}))
    skills = await S.combat_skills(db, 1)
    assert skills == {"kim_than": 0.5, "thanh_khu": 1.0}


async def test_combat_skills_the_chat_thuong_khong_them_noi_tai(monkeypatch, db):
    from src.features.the_chat import service as the_chat
    from src.features.thien_phu import service as thien_phu

    monkeypatch.setattr(thien_phu, "get_thien_phu_skills", AsyncMock(return_value={"kim_than": 0.5}))
    monkeypatch.setattr(the_chat, "get_the_chat_row", AsyncMock(return_value={"key": "the_chat_pham"}))
    assert await S.combat_skills(db, 1) == {"kim_than": 0.5}


async def test_combat_skills_van_hoat_dong_khi_doc_the_chat_loi(monkeypatch, db):
    from src.features.the_chat import service as the_chat
    from src.features.thien_phu import service as thien_phu

    original = {"bat_khuat": 1.0}
    monkeypatch.setattr(thien_phu, "get_thien_phu_skills", AsyncMock(return_value=original))
    monkeypatch.setattr(the_chat, "get_the_chat_row", AsyncMock(side_effect=RuntimeError("hỏng")))
    result = await S.combat_skills(db, 1)
    assert result == {"bat_khuat": 1.0}
    assert result is not original


@pytest.mark.parametrize("the_chat_key", list(S.THE_CHAT_SKILLS))
async def test_moi_the_chat_thuong_pham_duoc_cong_noi_tai_tuong_ung(monkeypatch, db, the_chat_key):
    from src.features.the_chat import service as the_chat
    from src.features.thien_phu import service as thien_phu

    monkeypatch.setattr(thien_phu, "get_thien_phu_skills", AsyncMock(return_value={}))
    monkeypatch.setattr(the_chat, "get_the_chat_row", AsyncMock(return_value={"key": the_chat_key}))
    assert await S.combat_skills(db, 1) == {S.THE_CHAT_SKILLS[the_chat_key]["skill"]: 1.0}
