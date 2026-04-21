"""Tests for envault.cli_backup CLI commands."""

import json
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.cli_backup import backup_cli


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def fake_backup_path(tmp_path):
    """Create a minimal .evbak file for restore/delete tests."""
    bak = tmp_path / "myvault_20240101T000000Z.evbak"
    meta = {"vault": "myvault", "created_at": "20240101T000000Z", "source": "/fake"}
    with zipfile.ZipFile(bak, "w") as zf:
        zf.writestr("vault.enc", b"encrypted-data")
        zf.writestr("meta.json", json.dumps(meta))
    return bak


def test_backup_create_success(runner, tmp_path):
    with patch("envault.cli_backup.create_backup") as mock_create:
        mock_create.return_value = tmp_path / "myvault_ts.evbak"
        result = runner.invoke(backup_cli, ["create", "myvault", "--dest", str(tmp_path)])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_backup_create_vault_not_found(runner):
    from envault.backup import BackupError
    with patch("envault.cli_backup.create_backup", side_effect=BackupError("does not exist")):
        result = runner.invoke(backup_cli, ["create", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_backup_list_shows_entries(runner, tmp_path):
    entries = [
        {"filename": "myvault_A.evbak", "created_at": "20240202T120000Z", "path": "/a"},
        {"filename": "myvault_B.evbak", "created_at": "20240101T120000Z", "path": "/b"},
    ]
    with patch("envault.cli_backup.list_backups", return_value=entries):
        result = runner.invoke(backup_cli, ["list", "myvault"])
    assert result.exit_code == 0
    assert "myvault_A.evbak" in result.output
    assert "myvault_B.evbak" in result.output


def test_backup_list_empty(runner):
    with patch("envault.cli_backup.list_backups", return_value=[]):
        result = runner.invoke(backup_cli, ["list", "myvault"])
    assert result.exit_code == 0
    assert "No backups found" in result.output


def test_backup_restore_success(runner, fake_backup_path):
    with patch("envault.cli_backup.restore_backup", return_value="myvault") as mock_r:
        result = runner.invoke(backup_cli, ["restore", str(fake_backup_path)])
    assert result.exit_code == 0
    assert "restored" in result.output


def test_backup_restore_missing_file(runner, tmp_path):
    from envault.backup import BackupError
    with patch("envault.cli_backup.restore_backup", side_effect=BackupError("not found")):
        result = runner.invoke(backup_cli, ["restore", str(tmp_path / "ghost.evbak")])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_backup_delete_success(runner, fake_backup_path):
    with patch("envault.cli_backup.delete_backup") as mock_del:
        result = runner.invoke(backup_cli, ["delete", str(fake_backup_path)])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_backup_delete_missing(runner, tmp_path):
    from envault.backup import BackupError
    with patch("envault.cli_backup.delete_backup", side_effect=BackupError("not found")):
        result = runner.invoke(backup_cli, ["delete", str(tmp_path / "missing.evbak")])
    assert result.exit_code == 1
    assert "Error" in result.output
