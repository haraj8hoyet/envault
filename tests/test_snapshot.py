"""Tests for envault.snapshot module."""

import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.vault import Vault
from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    SnapshotError,
)


@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.storage.VAULT_DIR", tmp_path)
    monkeypatch.setattr("envault.snapshot._snapshot_dir",
                        lambda name: _patched_snapshot_dir(name, tmp_path))
    return tmp_path


def _patched_snapshot_dir(vault_name: str, base: Path) -> Path:
    d = base / vault_name / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _make_vault(tmp_vault_dir, name="myapp", password="secret"):
    vault = Vault.create(name, password)
    vault.set("DB_URL", "postgres://localhost/db")
    vault.set("API_KEY", "abc123")
    vault.save()
    return vault


def test_create_snapshot_returns_filename(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    filename = create_snapshot("myapp", "secret")
    assert filename.endswith(".json")


def test_create_snapshot_with_label(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    filename = create_snapshot("myapp", "secret", label="before-deploy")
    assert "before-deploy" in filename


def test_list_snapshots_returns_metadata(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    create_snapshot("myapp", "secret", label="v1")
    create_snapshot("myapp", "secret", label="v2")
    snapshots = list_snapshots("myapp")
    assert len(snapshots) == 2
    assert all("filename" in s for s in snapshots)
    assert all(s["keys"] == 2 for s in snapshots)


def test_list_snapshots_empty(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    assert list_snapshots("myapp") == []


def test_restore_snapshot_brings_back_data(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    filename = create_snapshot("myapp", "secret")
    # Overwrite a key after snapshot
    vault = Vault.open("myapp", "secret")
    vault.set("API_KEY", "changed")
    vault.save()
    count = restore_snapshot("myapp", "secret", filename)
    assert count == 2
    restored = Vault.open("myapp", "secret")
    assert restored.get("API_KEY") == "abc123"


def test_restore_snapshot_not_found(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot("myapp", "secret", "nonexistent.json")


def test_delete_snapshot(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    filename = create_snapshot("myapp", "secret")
    delete_snapshot("myapp", filename)
    assert list_snapshots("myapp") == []


def test_delete_snapshot_not_found(tmp_vault_dir):
    _make_vault(tmp_vault_dir)
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot("myapp", "ghost.json")
