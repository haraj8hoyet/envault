"""Tests for envault.diff module."""

import pytest
from unittest.mock import MagicMock
from envault.diff import diff_dicts, diff_vaults, diff_vault_env, DiffResult


def _mock_vault(data: dict):
    vault = MagicMock()
    vault.keys.return_value = list(data.keys())
    vault.get.side_effect = lambda k: data[k]
    return vault


def test_diff_dicts_added():
    result = diff_dicts({"A": "1"}, {"A": "1", "B": "2"})
    assert result.added == {"B": "2"}
    assert result.removed == {}
    assert result.changed == {}


def test_diff_dicts_removed():
    result = diff_dicts({"A": "1", "B": "2"}, {"A": "1"})
    assert result.removed == {"B": "2"}
    assert result.added == {}


def test_diff_dicts_changed():
    result = diff_dicts({"A": "old"}, {"A": "new"})
    assert result.changed == {"A": ("old", "new")}


def test_diff_dicts_unchanged():
    result = diff_dicts({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    assert sorted(result.unchanged) == ["A", "B"]
    assert not result.has_changes


def test_has_changes_true():
    result = diff_dicts({"A": "1"}, {"B": "2"})
    assert result.has_changes


def test_diff_vaults():
    vault_a = _mock_vault({"KEY1": "val1", "KEY2": "val2"})
    vault_b = _mock_vault({"KEY1": "val1", "KEY3": "val3"})
    result = diff_vaults(vault_a, vault_b)
    assert result.added == {"KEY3": "val3"}
    assert result.removed == {"KEY2": "val2"}
    assert "KEY1" in result.unchanged


def test_diff_vault_env_missing_in_env():
    vault = _mock_vault({"MY_VAR": "secret"})
    result = diff_vault_env(vault, env={})
    assert "MY_VAR" in result.removed


def test_diff_vault_env_match():
    vault = _mock_vault({"MY_VAR": "hello"})
    result = diff_vault_env(vault, env={"MY_VAR": "hello"})
    assert "MY_VAR" in result.unchanged
    assert not result.has_changes


def test_diff_vault_env_changed():
    vault = _mock_vault({"MY_VAR": "old"})
    result = diff_vault_env(vault, env={"MY_VAR": "new"})
    assert result.changed == {"MY_VAR": ("old", "new")}
