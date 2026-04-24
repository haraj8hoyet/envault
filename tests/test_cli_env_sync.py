"""Tests for envault.cli_env_sync."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envault.cli_env_sync import sync_cli


@pytest.fixture()
def runner():
    return CliRunner()


def _mock_vault(data: dict):
    vault = MagicMock()
    vault.keys.return_value = list(data.keys())
    vault.has.side_effect = lambda k: k in data
    vault.get.side_effect = lambda k: data[k]
    vault.set.side_effect = lambda k, v: data.update({k: v})
    return vault


@pytest.fixture()
def patch_vault_dir(tmp_path):
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        yield tmp_path


def test_sync_load_prints_export_statements(runner, patch_vault_dir):
    vault = _mock_vault({"FOO": "bar", "BAZ": "qux"})
    with patch("envault.cli_env_sync.vault_exists", return_value=True), \
         patch("envault.cli_env_sync.Vault.open", return_value=vault), \
         patch("envault.cli_env_sync.load_into_env") as mock_load:
        from envault.env_sync import SyncResult
        mock_load.return_value = SyncResult(loaded=["FOO", "BAZ"])
        result = runner.invoke(sync_cli, ["load", "myvault", "--password", "secret"])
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "BAZ" in result.output


def test_sync_load_vault_not_found(runner):
    with patch("envault.cli_env_sync.vault_exists", return_value=False):
        result = runner.invoke(sync_cli, ["load", "ghost", "--password", "x"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_sync_load_sync_error_shown(runner):
    vault = _mock_vault({})
    with patch("envault.cli_env_sync.vault_exists", return_value=True), \
         patch("envault.cli_env_sync.Vault.open", return_value=vault), \
         patch("envault.cli_env_sync.load_into_env", side_effect=Exception("boom")):
        result = runner.invoke(sync_cli, ["load", "myvault", "--password", "s"])
    assert result.exit_code != 0


def test_sync_push_writes_to_vault(runner):
    data = {}
    vault = _mock_vault(data)
    with patch("envault.cli_env_sync.vault_exists", return_value=True), \
         patch("envault.cli_env_sync.Vault.open", return_value=vault), \
         patch("envault.cli_env_sync.export_from_env") as mock_export:
        from envault.env_sync import SyncResult
        mock_export.return_value = SyncResult(exported=["FOO"], skipped=[])
        result = runner.invoke(sync_cli, ["push", "myvault", "--password", "secret"])
    assert result.exit_code == 0
    assert "pushed" in result.output
    vault.save.assert_called_once()


def test_sync_push_vault_not_found(runner):
    with patch("envault.cli_env_sync.vault_exists", return_value=False):
        result = runner.invoke(sync_cli, ["push", "ghost", "--password", "x"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_sync_push_shows_skipped(runner):
    vault = _mock_vault({})
    with patch("envault.cli_env_sync.vault_exists", return_value=True), \
         patch("envault.cli_env_sync.Vault.open", return_value=vault), \
         patch("envault.cli_env_sync.export_from_env") as mock_export:
        from envault.env_sync import SyncResult
        mock_export.return_value = SyncResult(exported=[], skipped=["EXISTING"])
        result = runner.invoke(sync_cli, ["push", "myvault", "--password", "s"])
    assert "skipped" in result.output
