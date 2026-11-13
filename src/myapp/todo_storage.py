import json
import os
from pathlib import Path


def get_data_dir():
    return Path(os.environ.get("APP_DATA_DIR", "data"))


class TodoList:
    def __init__(self):
        self.items = []

    def add(self, title):
        title = title.strip()
        if not title:
            raise ValueError("Tên công việc không được rỗng")
        self.items.append({"title": title, "done": False})

    def complete(self, index):
        self.items[index]["done"] = True

    def pending(self):
        return [t for t in self.items if not t["done"]]

    def save(self, filename="todo.json"):
        folder = get_data_dir()
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / filename
        path.write_text(json.dumps(self.items, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, filename="todo.json"):
        path = get_data_dir() / filename
        todo = cls()
        if path.exists():
            todo.items = json.loads(path.read_text(encoding="utf-8"))
        return todo
