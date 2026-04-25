"""Tests for envault/env_format.py"""

import pytest
from unittest.mock import MagicMock
from envault.env_format import (
    normalize_key,
    strip_value,
    format_vault,
    FormatResult,
)


def _make_vault(data: dict):
    vault = MagicMock()
    store = dict(data)
    vault.keys.side_effect = lambda: list(store.keys())
    vault.get.side_effect = lambda k: store[k]

    def _set(k, v):
        store[k] = v

    def _delete(k):
        del store[k]

    vault.set.side_effect = _set
    vault.delete.side_effect = _delete
    vault._store = store
    return vault


def test_normalize_key_uppercase():
    assert normalize_key("my_key") == "MY_KEY"


def test_normalize_key_replaces_spaces():
    assert normalize_key("my key") == "MY_KEY"


def test_normalize_key_replaces_hyphens():
    assert normalize_key("my-key") == "MY_KEY"


def test_normalize_key_strips_whitespace():
    assert normalize_key("  KEY  ") == "KEY"


def test_strip_value_removes_whitespace():
    assert strip_value("  hello  ") == "hello"


def test_strip_value_no_change():
    assert strip_value("hello") == "hello"


def test_format_vault_normalizes_key():
    vault = _make_vault({"my-key": "value"})
    result = format_vault(vault, normalize_keys=True, strip_values=False)
    assert result.has_changes
    assert "MY_KEY" in vault._store
    assert "my-key" not in vault._store


def test_format_vault_strips_value():
    vault = _make_vault({"KEY": "  value  "})
    result = format_vault(vault, normalize_keys=False, strip_values=True)
    assert result.has_changes
    assert vault._store["KEY"] == "value"


def test_format_vault_no_changes_when_already_clean():
    vault = _make_vault({"KEY": "value"})
    result = format_vault(vault, normalize_keys=True, strip_values=True)
    assert not result.has_changes
    assert "KEY" in result.skipped


def test_format_vault_dry_run_does_not_modify():
    vault = _make_vault({"my-key": "  value  "})
    result = format_vault(vault, normalize_keys=True, strip_values=True, dry_run=True)
    assert result.has_changes
    assert "my-key" in vault._store
    assert "MY_KEY" not in vault._store


def test_format_result_summary_contains_count():
    vault = _make_vault({"bad-key": "  val  ", "GOOD": "clean"})
    result = format_vault(vault)
    summary = result.summary()
    assert "1 change" in summary
    assert "1 skipped" in summary


def test_format_vault_multiple_keys():
    vault = _make_vault({"a-b": "x", "c-d": "y", "FINE": "ok"})
    result = format_vault(vault)
    assert len(result.changes) == 2
    assert len(result.skipped) == 1
