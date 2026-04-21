"""Tests for envault.cli_history CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envault.cli_history import history_cli


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def patch_vault_exists():
    with patch("envault.cli_history.vault_exists", return_value=True) as m:
        yield m


def test_history_show_lists_entries(runner, patch_vault_exists):
    entries = [
        {"timestamp": "2024-01-01T00:00:00+00:00", "key": "API_KEY", "value": "old"},
        {"timestamp": "2024-01-02T00:00:00+00:00", "key": "API_KEY", "value": "new"},
    ]
    with patch("envault.cli_history.get_history", return_value=entries):
        result = runner.invoke(history_cli, ["show", "myvault", "API_KEY"])
    assert result.exit_code == 0
    assert "old" in result.output
    assert "new" in result.output


def test_history_show_no_entries(runner, patch_vault_exists):
    with patch("envault.cli_history.get_history", return_value=[]):
        result = runner.invoke(history_cli, ["show", "myvault", "MISSING"])
    assert result.exit_code == 0
    assert "No history" in result.output


def test_history_show_vault_not_found(runner):
    with patch("envault.cli_history.vault_exists", return_value=False):
        result = runner.invoke(history_cli, ["show", "ghost", "KEY"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_history_list_keys(runner, patch_vault_exists):
    with patch("envault.cli_history.list_keys_with_history", return_value=["ALPHA", "BETA"]):
        result = runner.invoke(history_cli, ["list", "myvault"])
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output


def test_history_list_empty(runner, patch_vault_exists):
    with patch("envault.cli_history.list_keys_with_history", return_value=[]):
        result = runner.invoke(history_cli, ["list", "myvault"])
    assert result.exit_code == 0
    assert "No history" in result.output


def test_history_clear_key(runner, patch_vault_exists):
    with patch("envault.cli_history.clear_history") as mock_clear:
        result = runner.invoke(history_cli, ["clear", "myvault", "API_KEY"], input="y\n")
    assert result.exit_code == 0
    mock_clear.assert_called_once_with("myvault", "API_KEY")
    assert "cleared" in result.output


def test_history_show_respects_limit(runner, patch_vault_exists):
    entries = [
        {"timestamp": f"2024-01-0{i}T00:00:00+00:00", "key": "K", "value": f"v{i}"}
        for i in range(1, 6)
    ]
    with patch("envault.cli_history.get_history", return_value=entries):
        result = runner.invoke(history_cli, ["show", "myvault", "K", "--limit", "2"])
    assert result.exit_code == 0
    assert "v4" in result.output
    assert "v5" in result.output
    assert "v1" not in result.output
