import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

DEFAULT_GAME = Path(r"C:\Users\pc\Documents\My Web Sites\tt")
GAME = Path(os.environ.get("TUTIEN_HOME", DEFAULT_GAME)).resolve()
DATA = Path(os.environ.get("TUTIEN_DATA", GAME.parent / "tsq_data")).resolve()
HERE = Path(__file__).resolve().parent

if not (GAME / "src").is_dir():
    raise pytest.UsageError(
        f"Không tìm thấy mã nguồn game tại {GAME}. Đặt biến môi trường TUTIEN_HOME trỏ tới thư mục chứa app.py và src/."
    )

sys.path.insert(0, str(GAME))
os.environ["TUTIEN_HOME"] = str(GAME)

_TMP_DATA = tempfile.mkdtemp(prefix="tutien_test_")
os.environ["TU_TIEN_DATA_DIR"] = _TMP_DATA
os.environ["TU_TIEN_DATABASE_PATH"] = "test.db"
os.environ.setdefault("TU_TIEN_BACKUP_INTERVAL_HOURS", "24")


@pytest.fixture(scope="session")
def game_home() -> Path:
    return GAME


@pytest.fixture(scope="session")
def tmp_data_dir() -> str:
    return _TMP_DATA


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from app import app

    browser_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "accept-language": "vi-VN,vi;q=0.9",
    }
    with TestClient(app, headers=browser_headers) as c:
        yield c


@pytest.fixture(scope="session")
def real_db_copy(tmp_path_factory) -> Path:
    src = DATA / "tutien.db"
    if not src.exists():
        pytest.skip(f"Không có dữ liệu tại {src} (đặt TUTIEN_DATA để trỏ tới thư mục tsq_data)")
    dest = tmp_path_factory.mktemp("tsq_copy") / "tutien_copy.db"
    source = sqlite3.connect(f"file:{src.as_posix()}?mode=ro", uri=True, timeout=30)
    target = sqlite3.connect(dest)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return dest


@pytest.fixture(scope="session")
def conn(real_db_copy):
    c = sqlite3.connect(f"file:{real_db_copy.as_posix()}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


@pytest.fixture(scope="session")
def q(conn):
    def run(sql, *args):
        return conn.execute(sql, args).fetchall()

    return run


@pytest.fixture(scope="session")
def scalar(conn):
    def run(sql, *args):
        row = conn.execute(sql, args).fetchone()
        return row[0] if row else None

    return run
