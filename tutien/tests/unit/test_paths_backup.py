import os
import sqlite3
import time
from pathlib import Path

import pytest

from src.core import config, db_backup, paths

pytestmark = pytest.mark.unit


def make_db(path: Path, rows: int = 3) -> Path:
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE nguoi_choi (user_id INTEGER PRIMARY KEY, ten TEXT, linh_thach INTEGER)")
    con.executemany("INSERT INTO nguoi_choi VALUES (?, ?, ?)", [(i, f"nv{i}", i * 100) for i in range(1, rows + 1)])
    con.commit()
    con.close()
    return path


def count_rows(path: Path) -> int:
    con = sqlite3.connect(path)
    try:
        return con.execute("SELECT COUNT(*) FROM nguoi_choi").fetchone()[0]
    finally:
        con.close()


class TestPaths:
    def test_data_dir_tuyet_doi(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config, "DATA_DIR", str(tmp_path))
        assert paths.data_dir() == tmp_path.resolve()

    def test_data_dir_tuong_doi_tinh_tu_thu_muc_code(self, monkeypatch):
        monkeypatch.setattr(config, "DATA_DIR", "../tsq_data")
        assert paths.data_dir() == (paths.BASE / "../tsq_data").resolve()

    def test_khong_dat_data_dir_thi_dung_thu_muc_code(self, monkeypatch):
        monkeypatch.setattr(config, "DATA_DIR", "")
        assert paths.data_dir() == paths.BASE

    def test_db_tuong_doi_tinh_tu_thu_muc_du_lieu(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config, "DATA_DIR", str(tmp_path))
        monkeypatch.setattr(config, "DATABASE_PATH", "tutien.db")
        assert paths.db_path() == (tmp_path / "tutien.db").resolve()

    def test_db_tuyet_doi_duoc_giu_nguyen(self, monkeypatch, tmp_path):
        target = tmp_path / "khac" / "game.db"
        monkeypatch.setattr(config, "DATABASE_PATH", str(target))
        assert paths.db_path() == target.resolve()

    def test_database_path_rong_dung_ten_mac_dinh(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config, "DATA_DIR", str(tmp_path))
        monkeypatch.setattr(config, "DATABASE_PATH", "")
        assert paths.db_path().name == "tutien.db"

    def test_thu_muc_sao_luu_va_nhat_ky_nam_canh_db(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config, "DATA_DIR", str(tmp_path))
        monkeypatch.setattr(config, "DATABASE_PATH", "tutien.db")
        assert paths.backup_dir() == tmp_path.resolve() / ".backups"
        assert paths.log_dir() == tmp_path.resolve() / "logs"


class TestEnvInt:
    def test_doc_so_nguyen_tu_moi_truong(self, monkeypatch):
        monkeypatch.setenv("TT_DEMO_INT", "42")
        assert config._env_int("TT_DEMO_INT", 7) == 42

    def test_thieu_bien_thi_dung_mac_dinh(self, monkeypatch):
        monkeypatch.delenv("TT_DEMO_INT", raising=False)
        assert config._env_int("TT_DEMO_INT", 7) == 7

    def test_gia_tri_khong_phai_so_thi_dung_mac_dinh(self, monkeypatch):
        monkeypatch.setenv("TT_DEMO_INT", "abc")
        assert config._env_int("TT_DEMO_INT", 7) == 7

    def test_khong_nho_hon_gia_tri_toi_thieu(self, monkeypatch):
        monkeypatch.setenv("TT_DEMO_INT", "-5")
        assert config._env_int("TT_DEMO_INT", 7, minimum=1) == 1


class TestBackup:
    def test_tao_ban_sao_dung_du_lieu(self, tmp_path):
        src = make_db(tmp_path / "tutien.db", rows=5)
        dest = db_backup.backup_now(src, tmp_path / ".backups")
        assert dest is not None and dest.exists()
        assert dest.name.startswith("tutien_") and dest.suffix == ".db"
        assert count_rows(dest) == 5

    def test_ban_sao_doc_lap_voi_ban_goc(self, tmp_path):
        src = make_db(tmp_path / "tutien.db")
        dest = db_backup.backup_now(src, tmp_path / ".backups")
        con = sqlite3.connect(src)
        con.execute("DELETE FROM nguoi_choi")
        con.commit()
        con.close()
        assert count_rows(dest) == 3

    def test_khong_co_db_thi_tra_ve_none(self, tmp_path):
        assert db_backup.backup_now(tmp_path / "khong_co.db", tmp_path / ".backups") is None

    def test_db_rong_khong_duoc_sao_luu(self, tmp_path):
        empty = tmp_path / "tutien.db"
        empty.write_bytes(b"")
        assert db_backup.backup_now(empty, tmp_path / ".backups") is None

    def test_khong_de_lai_file_tam(self, tmp_path):
        src = make_db(tmp_path / "tutien.db")
        db_backup.backup_now(src, tmp_path / ".backups")
        assert list((tmp_path / ".backups").glob("*.tmp")) == []

    def test_chep_them_ban_thu_hai_sang_thu_muc_mirror(self, tmp_path):
        src = make_db(tmp_path / "tutien.db")
        dest = db_backup.backup_now(src, tmp_path / ".backups", mirror_dir=tmp_path / "mirror")
        assert (tmp_path / "mirror" / dest.name).exists()

    def test_nguon_ghi_khong_bi_sua_boi_sao_luu(self, tmp_path):
        src = make_db(tmp_path / "tutien.db", rows=4)
        before = count_rows(src)
        db_backup.backup_now(src, tmp_path / ".backups")
        assert count_rows(src) == before == 4

    def test_don_ban_cu_nhung_luon_giu_toi_thieu_3_ban(self, tmp_path):
        folder = tmp_path / ".backups"
        folder.mkdir()
        old = time.time() - 90 * 86400
        for i in range(6):
            f = folder / f"tutien_2020010{i}_000000.db"
            f.write_bytes(b"x")
            os.utime(f, (old - i, old - i))
        removed = db_backup._prune(folder, "tutien", keep_days=14)
        assert removed == 3
        assert len(list(folder.glob("tutien_*.db"))) == db_backup.MIN_KEEP

    def test_khong_xoa_ban_con_han(self, tmp_path):
        folder = tmp_path / ".backups"
        folder.mkdir()
        for i in range(6):
            (folder / f"tutien_2026010{i}_000000.db").write_bytes(b"x")
        assert db_backup._prune(folder, "tutien", keep_days=14) == 0

    def test_chi_don_dung_tien_to_cua_db(self, tmp_path):
        folder = tmp_path / ".backups"
        folder.mkdir()
        old = time.time() - 90 * 86400
        for name in ("khac_20200101_000000.db", "tutien_20200101_000000.db"):
            f = folder / name
            f.write_bytes(b"x")
            os.utime(f, (old, old))
        db_backup._prune(folder, "tutien", keep_days=14)
        assert (folder / "khac_20200101_000000.db").exists()


class TestAdoptLegacy:
    def test_chuyen_db_cu_khi_noi_moi_chua_co(self, tmp_path):
        (tmp_path / "code").mkdir()
        legacy = make_db(tmp_path / "code" / "tutien.db")
        target = tmp_path / "tsq_data" / "tutien.db"
        assert db_backup.adopt_legacy_db(legacy, target) is True
        assert count_rows(target) == 3 and legacy.exists()

    def test_khong_bao_gio_ghi_de_db_dang_co(self, tmp_path):
        (tmp_path / "code").mkdir()
        legacy = make_db(tmp_path / "code" / "tutien.db", rows=1)
        (tmp_path / "tsq_data").mkdir()
        target = make_db(tmp_path / "tsq_data" / "tutien.db", rows=9)
        assert db_backup.adopt_legacy_db(legacy, target) is False
        assert count_rows(target) == 9

    def test_khong_co_db_cu_thi_khong_lam_gi(self, tmp_path):
        assert db_backup.adopt_legacy_db(tmp_path / "khong_co.db", tmp_path / "moi.db") is False
        assert not (tmp_path / "moi.db").exists()

    def test_cung_mot_file_thi_bo_qua(self, tmp_path):
        db = make_db(tmp_path / "tutien.db")
        assert db_backup.adopt_legacy_db(db, db) is False
