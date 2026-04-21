"""Tests for envault.backup module."""

import json
import zipfile
from pathlib import Path

import pytest

from envault.backup import (
    BackupError,
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
)
from envault.vault import Vault


@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    import envault.storage as storage
    monkeypatch.setattr(storage, "_base_dir", lambda: tmp_path)
    return tmp_path


def _make_vault(tmp_vault_dir, name="myvault", password="secret"):
    v = Vault.create(name, password)
    v.set("KEY", "value")
    v.save()
    return v


def test_create_backup_returns_path(tmp_vault_dir, tmp_path):
    _make_vault(tmp_vault_dir)
    backup_dir = tmp_path / "backups"
    path = create_backup("myvault", backup_dir)
    assert path.exists()
    assert path.suffix == ".evbak"


def test_create_backup_is_valid_zip(tmp_vault_dir, tmp_path):
    _make_vault(tmp_vault_dir)
    backup_dir = tmp_path / "backups"
    path = create_backup("myvault", backup_dir)
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
    assert "vault.enc" in names
    assert "meta.json" in names


def test_create_backup_meta_contains_vault_name(tmp_vault_dir, tmp_path):
    _make_vault(tmp_vault_dir)
    backup_dir = tmp_path / "backups"
    path = create_backup("myvault", backup_dir)
    with zipfile.ZipFile(path, "r") as zf:
        meta = json.loads(zf.read("meta.json"))
    assert meta["vault"] == "myvault"


def test_create_backup_nonexistent_vault_raises(tmp_vault_dir, tmp_path):
    with pytest.raises(BackupError, match="does not exist"):
        create_backup("ghost", tmp_path / "backups")


def test_list_backups_returns_entries(tmp_vault_dir, tmp_path):
    _make_vault(tmp_vault_dir)
    backup_dir = tmp_path / "backups"
    create_backup("myvault", backup_dir)
    create_backup("myvault", backup_dir)
    backups = list_backups("myvault", backup_dir)
    assert len(backups) == 2


def test_list_backups_empty_when_no_dir(tmp_path):
    result = list_backups("myvault", tmp_path / "nonexistent")
    assert result == []


def test_restore_backup_recreates_vault_file(tmp_vault_dir, tmp_path):
    _make_vault(tmp_vault_dir)
    backup_dir = tmp_path / "backups"
    bak_path = create_backup("myvault", backup_dir)

    # Remove original vault file
    from envault.storage import _vault_path
    _vault_path("myvault").unlink()

    restored_name = restore_backup(bak_path)
    assert restored_name == "myvault"
    assert _vault_path("myvault").exists()


def test_restore_backup_with_override_name(tmp_vault_dir, tmp_path):
    _make_vault(tmp_vault_dir)
    backup_dir = tmp_path / "backups"
    bak_path = create_backup("myvault", backup_dir)

    restored_name = restore_backup(bak_path, vault_name="newvault")
    assert restored_name == "newvault"
    from envault.storage import _vault_path
    assert _vault_path("newvault").exists()


def test_restore_missing_backup_raises(tmp_path):
    with pytest.raises(BackupError, match="not found"):
        restore_backup(tmp_path / "ghost.evbak")


def test_delete_backup_removes_file(tmp_vault_dir, tmp_path):
    _make_vault(tmp_vault_dir)
    backup_dir = tmp_path / "backups"
    bak_path = create_backup("myvault", backup_dir)
    assert bak_path.exists()
    delete_backup(bak_path)
    assert not bak_path.exists()


def test_delete_nonexistent_backup_raises(tmp_path):
    with pytest.raises(BackupError, match="not found"):
        delete_backup(tmp_path / "missing.evbak")
