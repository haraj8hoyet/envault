"""Tests for envault/cli_search.py."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_search import search_cli


@pytest.fixture
def runner():
    return CliRunner()


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "topsecret",
}


def _mock_vault(data):
    v = MagicMock()
    v.all.return_value = data
    return v


@patch("envault.cli_search.vault_exists", return_value=True)
@patch("envault.cli_search.Vault.open")
def test_search_keys_command(mock_open, mock_exists, runner):
    mock_open.return_value = _mock_vault(SAMPLE)
    result = runner.invoke(search_cli, ["keys", "myvault", "DB_*", "--password", "pass"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PORT" in result.output
    assert "APP_SECRET" not in result.output


@patch("envault.cli_search.vault_exists", return_value=True)
@patch("envault.cli_search.Vault.open")
def test_search_keys_no_match(mock_open, mock_exists, runner):
    mock_open.return_value = _mock_vault(SAMPLE)
    result = runner.invoke(search_cli, ["keys", "myvault", "MISSING_*", "--password", "pass"])
    assert result.exit_code == 0
    assert "No matching keys found" in result.output


@patch("envault.cli_search.vault_exists", return_value=False)
def test_search_keys_vault_not_found(mock_exists, runner):
    result = runner.invoke(search_cli, ["keys", "ghost", "DB_*", "--password", "pass"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


@patch("envault.cli_search.vault_exists", return_value=True)
@patch("envault.cli_search.Vault.open")
def test_search_values_command(mock_open, mock_exists, runner):
    mock_open.return_value = _mock_vault(SAMPLE)
    result = runner.invoke(search_cli, ["values", "myvault", "localhost", "--password", "pass"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


@patch("envault.cli_search.vault_exists", return_value=True)
@patch("envault.cli_search.Vault.open")
def test_search_prefix_command(mock_open, mock_exists, runner):
    mock_open.return_value = _mock_vault(SAMPLE)
    result = runner.invoke(search_cli, ["prefix", "myvault", "APP_", "--password", "pass"])
    assert result.exit_code == 0
    assert "APP_SECRET" in result.output
    assert "DB_HOST" not in result.output
