"""Tests for envault.env_check and envault.cli_env_check."""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envault.env_check import CheckIssue, CheckResult, check_vault_against_env
from envault.cli_env_check import check_cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_vault(data: dict) -> MagicMock:
    vault = MagicMock()
    vault.keys.return_value = list(data.keys())
    vault.get.side_effect = lambda k: data.get(k)
    return vault


# ---------------------------------------------------------------------------
# Unit tests — env_check module
# ---------------------------------------------------------------------------

def test_no_issues_when_env_matches(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    monkeypatch.setenv("BAZ", "qux")
    vault = _make_vault({"FOO": "bar", "BAZ": "qux"})
    result = check_vault_against_env(vault)
    assert not result.has_issues()


def test_missing_key_detected(monkeypatch):
    monkeypatch.delenv("MY_KEY", raising=False)
    vault = _make_vault({"MY_KEY": "secret"})
    result = check_vault_against_env(vault)
    assert len(result.by_kind("missing")) == 1
    assert result.by_kind("missing")[0].key == "MY_KEY"


def test_mismatch_detected(monkeypatch):
    monkeypatch.setenv("MY_KEY", "wrong")
    vault = _make_vault({"MY_KEY": "correct"})
    result = check_vault_against_env(vault)
    assert len(result.by_kind("mismatch")) == 1
    issue = result.by_kind("mismatch")[0]
    assert issue.vault_value == "correct"
    assert issue.env_value == "wrong"


def test_extra_reported_when_flag_set(monkeypatch):
    monkeypatch.setenv("EXTRA_VAR", "something")
    vault = _make_vault({})
    result = check_vault_against_env(vault, report_extra=True)
    extras = [i.key for i in result.by_kind("extra")]
    assert "EXTRA_VAR" in extras


def test_extra_not_reported_by_default(monkeypatch):
    monkeypatch.setenv("EXTRA_VAR", "something")
    vault = _make_vault({})
    result = check_vault_against_env(vault, report_extra=False)
    assert not result.by_kind("extra")


def test_keys_subset_limits_check(monkeypatch):
    monkeypatch.delenv("IGNORED", raising=False)
    monkeypatch.setenv("CHECKED", "ok")
    vault = _make_vault({"CHECKED": "ok", "IGNORED": "value"})
    result = check_vault_against_env(vault, keys=["CHECKED"])
    assert not result.has_issues()


def test_check_issue_str_missing():
    issue = CheckIssue(key="X", kind="missing", vault_value="v")
    assert "MISSING" in str(issue)
    assert "X" in str(issue)


def test_check_issue_str_mismatch():
    issue = CheckIssue(key="Y", kind="mismatch", vault_value="a", env_value="b")
    assert "MISMATCH" in str(issue)


def test_check_issue_str_extra():
    issue = CheckIssue(key="Z", kind="extra", env_value="val")
    assert "EXTRA" in str(issue)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def _mock_vault(data):
    v = _make_vault(data)
    return v


def test_cli_check_all_pass(runner, monkeypatch):
    monkeypatch.setenv("API_KEY", "abc")
    vault = _mock_vault({"API_KEY": "abc"})
    with patch("envault.cli_env_check.vault_exists", return_value=True), \
         patch("envault.cli_env_check.Vault.open", return_value=vault):
        result = runner.invoke(
            check_cli, ["run", "myvault", "--password", "pw"]
        )
    assert result.exit_code == 0
    assert "All checks passed" in result.output


def test_cli_check_reports_missing(runner, monkeypatch):
    monkeypatch.delenv("MISSING_KEY", raising=False)
    vault = _mock_vault({"MISSING_KEY": "val"})
    with patch("envault.cli_env_check.vault_exists", return_value=True), \
         patch("envault.cli_env_check.Vault.open", return_value=vault):
        result = runner.invoke(
            check_cli, ["run", "myvault", "--password", "pw"]
        )
    assert "MISSING" in result.output


def test_cli_check_strict_exits_nonzero(runner, monkeypatch):
    monkeypatch.delenv("SOME_KEY", raising=False)
    vault = _mock_vault({"SOME_KEY": "val"})
    with patch("envault.cli_env_check.vault_exists", return_value=True), \
         patch("envault.cli_env_check.Vault.open", return_value=vault):
        result = runner.invoke(
            check_cli, ["run", "myvault", "--password", "pw", "--strict"]
        )
    assert result.exit_code != 0


def test_cli_check_vault_not_found(runner):
    with patch("envault.cli_env_check.vault_exists", return_value=False):
        result = runner.invoke(
            check_cli, ["run", "ghost", "--password", "pw"]
        )
    assert result.exit_code != 0
    assert "not found" in result.output
