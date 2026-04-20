"""Tests for envault/cli_ttl.py"""

import time
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_ttl import ttl_cli


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data=None, meta_store=None):
    data = data or {"API_KEY": "secret"}
    meta_store = meta_store or {}
    v = MagicMock()
    v.has.side_effect = lambda k: k in data
    v.keys.side_effect = lambda: list(data.keys())
    v.get_meta.side_effect = lambda k: dict(meta_store.get(k, {}))
    def _set_meta(k, m):
        meta_store[k] = m
    v.set_meta.side_effect = _set_meta
    def _delete(k):
        data.pop(k, None)
    v.delete.side_effect = _delete
    return v


def test_ttl_set_command(runner):
    vault = _mock_vault()
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["set", "myvault", "API_KEY", "120", "--password", "pass"])
    assert result.exit_code == 0
    assert "120s" in result.output
    vault.save.assert_called_once()


def test_ttl_set_missing_key(runner):
    vault = _mock_vault()
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["set", "myvault", "NOPE", "60", "--password", "pass"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_ttl_get_no_ttl(runner):
    vault = _mock_vault()
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["get", "myvault", "API_KEY", "--password", "pass"])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_ttl_get_active(runner):
    meta_store = {"API_KEY": {"_ttl": 300, "_expires_at": time.time() + 300}}
    vault = _mock_vault(meta_store=meta_store)
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["get", "myvault", "API_KEY", "--password", "pass"])
    assert result.exit_code == 0
    assert "remaining" in result.output


def test_ttl_get_expired(runner):
    meta_store = {"API_KEY": {"_ttl": 1, "_expires_at": time.time() - 5}}
    vault = _mock_vault(meta_store=meta_store)
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["get", "myvault", "API_KEY", "--password", "pass"])
    assert result.exit_code == 0
    assert "expired" in result.output


def test_ttl_clear_command(runner):
    meta_store = {"API_KEY": {"_ttl": 60, "_expires_at": time.time() + 60}}
    vault = _mock_vault(meta_store=meta_store)
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["clear", "myvault", "API_KEY", "--password", "pass"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    vault.save.assert_called_once()


def test_ttl_purge_no_expired(runner):
    vault = _mock_vault()
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["purge", "myvault", "--password", "pass"])
    assert result.exit_code == 0
    assert "No expired" in result.output


def test_ttl_purge_with_expired(runner):
    data = {"OLD": "x", "NEW": "y"}
    meta_store = {
        "OLD": {"_ttl": 1, "_expires_at": time.time() - 10},
        "NEW": {"_ttl": 100, "_expires_at": time.time() + 100},
    }
    vault = _mock_vault(data=data, meta_store=meta_store)
    with patch("envault.cli_ttl.Vault.open", return_value=vault):
        result = runner.invoke(ttl_cli, ["purge", "myvault", "--password", "pass"])
    assert result.exit_code == 0
    assert "OLD" in result.output
    vault.save.assert_called_once()
