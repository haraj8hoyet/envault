"""Tests for envault.lint and envault.cli_lint."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from envault.lint import lint_vault, LintIssue, LintResult
from envault.cli_lint import lint_cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_vault(data: dict) -> MagicMock:
    vault = MagicMock()
    vault.keys.return_value = list(data.keys())
    vault.get.side_effect = lambda k: data[k]
    return vault


# ---------------------------------------------------------------------------
# Unit tests for lint_vault
# ---------------------------------------------------------------------------

def test_no_issues_for_clean_vault():
    vault = _make_fake_vault({"DATABASE_URL": "postgres://localhost/db"})
    result = lint_vault(vault)
    assert not result.issues
    assert not result.has_errors
    assert not result.has_warnings


def test_empty_value_is_error():
    vault = _make_fake_vault({"API_KEY": ""})
    result = lint_vault(vault)
    errors = result.errors()
    assert any(i.key == "API_KEY" and "empty" in i.message for i in errors)


def test_lowercase_key_is_warning():
    vault = _make_fake_vault({"api_key": "secret"})
    result = lint_vault(vault)
    warnings = result.warnings()
    assert any(i.key == "api_key" and "uppercase" in i.message for i in warnings)


def test_key_with_spaces_is_error():
    vault = _make_fake_vault({"BAD KEY": "value"})
    result = lint_vault(vault)
    errors = result.errors()
    assert any("spaces" in i.message for i in errors)


def test_placeholder_value_is_warning():
    vault = _make_fake_vault({"TOKEN": "<your-token-here>"})
    result = lint_vault(vault)
    warnings = result.warnings()
    assert any("placeholder" in i.message for i in warnings)


def test_long_value_is_info():
    vault = _make_fake_vault({"CERT": "x" * 501})
    result = lint_vault(vault)
    info_issues = [i for i in result.issues if i.severity == "info"]
    assert any("long" in i.message for i in info_issues)


def test_has_errors_property():
    result = LintResult(issues=[LintIssue("K", "error", "bad")])
    assert result.has_errors


def test_has_warnings_property():
    result = LintResult(issues=[LintIssue("K", "warning", "meh")])
    assert result.has_warnings
    assert not result.has_errors


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def _mock_vault(data):
    fake = _make_fake_vault(data)
    return fake


def test_cli_no_issues(runner):
    fake = _mock_vault({"PORT": "8080"})
    with patch("envault.cli_lint.vault_exists", return_value=True), \
         patch("envault.cli_lint.Vault.open", return_value=fake):
        result = runner.invoke(lint_cli, ["check", "myvault", "--password", "pass"])
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_cli_reports_error_and_exits_nonzero(runner):
    fake = _mock_vault({"bad key": ""})
    with patch("envault.cli_lint.vault_exists", return_value=True), \
         patch("envault.cli_lint.Vault.open", return_value=fake):
        result = runner.invoke(lint_cli, ["check", "myvault", "--password", "pass"])
    assert result.exit_code == 1
    assert "ERROR" in result.output


def test_cli_vault_not_found(runner):
    with patch("envault.cli_lint.vault_exists", return_value=False):
        result = runner.invoke(lint_cli, ["check", "ghost", "--password", "pass"])
    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_cli_strict_flag_exits_on_warnings(runner):
    fake = _mock_vault({"lower": "value"})
    with patch("envault.cli_lint.vault_exists", return_value=True), \
         patch("envault.cli_lint.Vault.open", return_value=fake):
        result = runner.invoke(
            lint_cli, ["check", "myvault", "--password", "pass", "--strict"]
        )
    assert result.exit_code == 1
