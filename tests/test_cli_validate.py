"""Tests for envault.cli_validate."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envault.cli_validate import validate_cli


@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data):
    vault = MagicMock()
    vault.keys.return_value = list(data.keys())
    vault.get.side_effect = lambda k: data.get(k, "")
    return vault


@pytest.fixture
def patch_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.cli_validate.vault_exists", lambda name: True)


def test_validate_check_all_pass(runner, patch_vault_dir):
    vault = _mock_vault({"API_KEY": "secret", "PORT": "8080"})
    with patch("envault.cli_validate.Vault.open", return_value=vault):
        result = runner.invoke(validate_cli, ["check", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "All checks passed" in result.output


def test_validate_check_missing_required(runner, patch_vault_dir):
    vault = _mock_vault({"PORT": "8080"})
    with patch("envault.cli_validate.Vault.open", return_value=vault):
        result = runner.invoke(
            validate_cli,
            ["check", "myvault", "--password", "pw", "--require", "API_KEY"],
        )
    assert result.exit_code == 2
    assert "API_KEY" in result.output


def test_validate_check_pattern_mismatch(runner, patch_vault_dir):
    vault = _mock_vault({"PORT": "abc"})
    with patch("envault.cli_validate.Vault.open", return_value=vault):
        result = runner.invoke(
            validate_cli,
            ["check", "myvault", "--password", "pw", "--pattern", r"PORT=\d+"],
        )
    assert result.exit_code == 2
    assert "PORT" in result.output


def test_validate_check_vault_not_found(runner):
    with patch("envault.cli_validate.vault_exists", return_value=False):
        result = runner.invoke(validate_cli, ["check", "missing", "--password", "pw"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_validate_check_schema_file(runner, patch_vault_dir, tmp_path):
    schema = {"required": ["TOKEN"], "patterns": {"PORT": r"\d+"}}
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema))

    vault = _mock_vault({"PORT": "9999"})
    with patch("envault.cli_validate.Vault.open", return_value=vault):
        result = runner.invoke(
            validate_cli,
            ["check", "myvault", "--password", "pw", "--schema", str(schema_file)],
        )
    assert result.exit_code == 2
    assert "TOKEN" in result.output


def test_validate_check_invalid_pattern_spec(runner, patch_vault_dir):
    vault = _mock_vault({"KEY": "val"})
    with patch("envault.cli_validate.Vault.open", return_value=vault):
        result = runner.invoke(
            validate_cli,
            ["check", "myvault", "--password", "pw", "--pattern", "NOEQUALS"],
        )
    assert result.exit_code == 1
    assert "Invalid pattern spec" in result.output
