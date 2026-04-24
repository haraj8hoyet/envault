"""Tests for envault.env_validate."""

import pytest
from envault.env_validate import validate_vault, ValidationIssue, ValidationResult


class _FakeVault:
    def __init__(self, data):
        self._data = data

    def keys(self):
        return list(self._data.keys())

    def get(self, key):
        return self._data.get(key, "")


def test_no_issues_for_valid_vault():
    vault = _FakeVault({"API_KEY": "abc123", "PORT": "8080"})
    result = validate_vault(vault)
    assert not result.has_errors()
    assert not result.has_warnings()
    assert result.issues == []


def test_missing_required_key_is_error():
    vault = _FakeVault({"PORT": "8080"})
    result = validate_vault(vault, required_keys=["API_KEY", "PORT"])
    assert result.has_errors()
    errors = result.errors()
    assert len(errors) == 1
    assert errors[0].key == "API_KEY"
    assert "missing" in errors[0].reason


def test_multiple_missing_keys_all_reported():
    vault = _FakeVault({})
    result = validate_vault(vault, required_keys=["A", "B", "C"])
    assert len(result.errors()) == 3


def test_empty_value_produces_warning_by_default():
    vault = _FakeVault({"KEY": ""})
    result = validate_vault(vault)
    assert result.has_warnings()
    assert not result.has_errors()
    assert result.warnings()[0].key == "KEY"


def test_allow_empty_suppresses_warning():
    vault = _FakeVault({"KEY": ""})
    result = validate_vault(vault, allow_empty=True)
    assert not result.has_warnings()
    assert not result.has_errors()


def test_pattern_match_passes():
    vault = _FakeVault({"PORT": "8080"})
    result = validate_vault(vault, patterns={"PORT": r"\d+"})
    assert not result.has_errors()


def test_pattern_mismatch_is_error():
    vault = _FakeVault({"PORT": "not-a-number"})
    result = validate_vault(vault, patterns={"PORT": r"\d+"})
    assert result.has_errors()
    assert result.errors()[0].key == "PORT"
    assert "pattern" in result.errors()[0].reason


def test_pattern_only_checked_for_existing_keys():
    vault = _FakeVault({})
    # KEY is absent; pattern should not trigger a pattern error (missing key error separate)
    result = validate_vault(vault, patterns={"KEY": r"\d+"})
    assert not result.has_errors()


def test_validation_issue_str():
    issue = ValidationIssue(key="FOO", reason="bad", severity="error")
    assert "[ERROR]" in str(issue)
    assert "FOO" in str(issue)
    assert "bad" in str(issue)


def test_combined_required_and_pattern():
    vault = _FakeVault({"URL": "not-a-url"})
    result = validate_vault(
        vault,
        required_keys=["URL", "TOKEN"],
        patterns={"URL": r"https?://.+"},
    )
    keys_with_errors = {i.key for i in result.errors()}
    assert "TOKEN" in keys_with_errors
    assert "URL" in keys_with_errors
