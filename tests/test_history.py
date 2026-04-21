"""Tests for envault.history module."""

from __future__ import annotations

import os
import pytest
from pathlib import Path

from envault.history import (
    record_change,
    get_history,
    clear_history,
    list_keys_with_history,
)


@pytest.fixture()
def tmp_history_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def test_record_and_get_single_entry(tmp_history_dir):
    record_change("myvault", "API_KEY", "secret123")
    entries = get_history("myvault", "API_KEY")
    assert len(entries) == 1
    assert entries[0]["key"] == "API_KEY"
    assert entries[0]["value"] == "secret123"
    assert "timestamp" in entries[0]


def test_record_multiple_entries_ordered(tmp_history_dir):
    record_change("myvault", "DB_PASS", "first")
    record_change("myvault", "DB_PASS", "second")
    record_change("myvault", "DB_PASS", "third")
    entries = get_history("myvault", "DB_PASS")
    assert len(entries) == 3
    assert [e["value"] for e in entries] == ["first", "second", "third"]


def test_record_with_actor(tmp_history_dir):
    record_change("myvault", "TOKEN", "abc", actor="alice")
    entries = get_history("myvault", "TOKEN")
    assert entries[0]["actor"] == "alice"


def test_get_history_empty_when_no_records(tmp_history_dir):
    result = get_history("myvault", "NONEXISTENT_KEY")
    assert result == []


def test_clear_history_removes_file(tmp_history_dir):
    record_change("myvault", "MY_KEY", "val1")
    assert len(get_history("myvault", "MY_KEY")) == 1
    clear_history("myvault", "MY_KEY")
    assert get_history("myvault", "MY_KEY") == []


def test_clear_history_nonexistent_key_is_noop(tmp_history_dir):
    clear_history("myvault", "GHOST_KEY")  # should not raise


def test_list_keys_with_history(tmp_history_dir):
    record_change("myvault", "ALPHA", "1")
    record_change("myvault", "BETA", "2")
    record_change("myvault", "GAMMA", "3")
    keys = list_keys_with_history("myvault")
    assert set(keys) == {"ALPHA", "BETA", "GAMMA"}


def test_list_keys_empty_when_no_history(tmp_history_dir):
    result = list_keys_with_history("empty_vault")
    assert result == []


def test_history_isolated_per_vault(tmp_history_dir):
    record_change("vault_a", "KEY", "from_a")
    record_change("vault_b", "KEY", "from_b")
    assert get_history("vault_a", "KEY")[0]["value"] == "from_a"
    assert get_history("vault_b", "KEY")[0]["value"] == "from_b"
