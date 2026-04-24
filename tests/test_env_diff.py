"""Tests for envault.env_diff."""
from __future__ import annotations

import pytest

from envault.env_diff import EnvDiffResult, diff_env


class _FakeVault:
    def __init__(self, data: dict) -> None:
        self._data = data

    def keys(self):
        return list(self._data.keys())

    def get(self, key: str):
        return self._data[key]


# ---------------------------------------------------------------------------
# diff_env
# ---------------------------------------------------------------------------

def test_match_when_values_equal():
    vault = _FakeVault({"FOO": "bar"})
    result = diff_env(vault, {"FOO": "bar"})
    assert len(result.entries) == 1
    assert result.entries[0].status == "match"
    assert not result.has_differences


def test_mismatch_when_values_differ():
    vault = _FakeVault({"FOO": "bar"})
    result = diff_env(vault, {"FOO": "baz"})
    assert result.entries[0].status == "mismatch"
    assert result.has_differences


def test_missing_in_env():
    vault = _FakeVault({"SECRET": "x"})
    result = diff_env(vault, {})
    assert result.entries[0].status == "missing_in_env"
    assert result.entries[0].vault_value == "x"
    assert result.entries[0].env_value is None


def test_missing_in_vault_not_reported_by_default():
    vault = _FakeVault({})
    result = diff_env(vault, {"EXTRA": "y"})
    assert result.entries == []


def test_missing_in_vault_reported_when_flag_set():
    vault = _FakeVault({})
    result = diff_env(vault, {"EXTRA": "y"}, include_extra=True)
    assert len(result.entries) == 1
    assert result.entries[0].status == "missing_in_vault"
    assert result.entries[0].env_value == "y"


def test_by_status_filter():
    vault = _FakeVault({"A": "1", "B": "2"})
    result = diff_env(vault, {"A": "1", "B": "WRONG"})
    matches = result.by_status("match")
    mismatches = result.by_status("mismatch")
    assert len(matches) == 1 and matches[0].key == "A"
    assert len(mismatches) == 1 and mismatches[0].key == "B"


def test_summary_string():
    vault = _FakeVault({"A": "1"})
    result = diff_env(vault, {"A": "2"})
    assert "mismatch" in result.summary()


def test_str_representations():
    vault = _FakeVault({"KEY": "val"})
    result = diff_env(vault, {}, include_extra=False)
    text = str(result.entries[0])
    assert "MISSING IN ENV" in text
    assert "KEY" in text


def test_empty_vault_empty_env():
    vault = _FakeVault({})
    result = diff_env(vault, {})
    assert result.entries == []
    assert not result.has_differences
    assert result.summary() == "no entries"
