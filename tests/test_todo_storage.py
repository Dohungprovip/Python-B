import json

import pytest

from myapp.todo_storage import TodoList, get_data_dir


def test_add_and_pending(todo):
    todo.add("  Học pytest ")
    todo.add("Viết báo cáo")
    todo.complete(0)
    assert [t["title"] for t in todo.pending()] == ["Viết báo cáo"]


def test_add_empty_title(todo):
    with pytest.raises(ValueError):
        todo.add("   ")


def test_default_data_dir(monkeypatch):
    monkeypatch.delenv("APP_DATA_DIR", raising=False)
    assert str(get_data_dir()) == "data"


def test_save_and_load_roundtrip(tmp_path, monkeypatch, todo):
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path))
    todo.add("Làm bài")
    todo.complete(0)

    path = todo.save()

    assert path.parent == tmp_path
    assert json.loads(path.read_text(encoding="utf-8"))[0]["done"] is True
    assert TodoList.load().items == todo.items


def test_load_missing_file_gives_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "chua_co"))
    assert TodoList.load().items == []
