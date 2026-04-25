"""Tests for envault.cli_group CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envault.cli_group import group_cli
from envault.env_group import META_GROUP_PREFIX


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data=None, meta=None):
    """Create a MagicMock vault with basic behaviour."""
    data = dict(data or {})
    meta = dict(meta or {})
    v = MagicMock()
    v.has.side_effect = lambda k: k in data
    v.keys.return_value = list(data.keys())
    v.get_meta.side_effect = lambda k: dict(meta.get(k, {}))
    v.set_meta.side_effect = lambda k, mk, mv: meta.setdefault(k, {}).__setitem__(mk, mv)
    v.delete_meta.side_effect = lambda k, mk: meta.get(k, {}).pop(mk, None)
    return v, meta


def _patch_vault(vault_mock):
    return patch("envault.cli_group.Vault.open", return_value=vault_mock)


def _patch_exists(exists=True):
    return patch("envault.cli_group.vault_exists", return_value=exists)


def test_group_assign_success(runner):
    v, meta = _mock_vault(data={"DB_HOST": "localhost"})
    with _patch_exists(), _patch_vault(v):
        result = runner.invoke(
            group_cli, ["assign", "myvault", "DB_HOST", "database", "--password", "pw"]
        )
    assert result.exit_code == 0
    assert "assigned to group 'database'" in result.output


def test_group_assign_vault_not_found(runner):
    with _patch_exists(False):
        result = runner.invoke(
            group_cli, ["assign", "missing", "KEY", "grp", "--password", "pw"]
        )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_group_assign_missing_key_shows_error(runner):
    v, _ = _mock_vault(data={})
    with _patch_exists(), _patch_vault(v):
        result = runner.invoke(
            group_cli, ["assign", "myvault", "GHOST", "grp", "--password", "pw"]
        )
    assert result.exit_code != 0


def test_group_list_all_groups(runner):
    meta = {
        "DB_HOST": {META_GROUP_PREFIX + "name": "database"},
        "APP_KEY": {META_GROUP_PREFIX + "name": "app"},
    }
    v, _ = _mock_vault(data={"DB_HOST": "x", "APP_KEY": "y"}, meta=meta)
    with _patch_exists(), _patch_vault(v):
        result = runner.invoke(group_cli, ["list", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "[database]" in result.output
    assert "[app]" in result.output


def test_group_list_filter_by_group(runner):
    meta = {
        "DB_HOST": {META_GROUP_PREFIX + "name": "database"},
        "APP_KEY": {META_GROUP_PREFIX + "name": "app"},
    }
    v, _ = _mock_vault(data={"DB_HOST": "x", "APP_KEY": "y"}, meta=meta)
    with _patch_exists(), _patch_vault(v):
        result = runner.invoke(
            group_cli, ["list", "myvault", "--group", "database", "--password", "pw"]
        )
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "APP_KEY" not in result.output


def test_group_rename_success(runner):
    meta = {
        "DB_HOST": {META_GROUP_PREFIX + "name": "database"},
        "DB_PASS": {META_GROUP_PREFIX + "name": "database"},
    }
    v, _ = _mock_vault(data={"DB_HOST": "x", "DB_PASS": "y"}, meta=meta)
    with _patch_exists(), _patch_vault(v):
        result = runner.invoke(
            group_cli, ["rename", "myvault", "database", "db", "--password", "pw"]
        )
    assert result.exit_code == 0
    assert "2 key(s) updated" in result.output


def test_group_unassign_success(runner):
    meta = {"MY_KEY": {META_GROUP_PREFIX + "name": "grp"}}
    v, _ = _mock_vault(data={"MY_KEY": "val"}, meta=meta)
    with _patch_exists(), _patch_vault(v):
        result = runner.invoke(
            group_cli, ["unassign", "myvault", "MY_KEY", "--password", "pw"]
        )
    assert result.exit_code == 0
    assert "removed" in result.output
