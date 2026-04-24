"""Tests for envault.env_sync."""

from __future__ import annotations

import os
import pytest

from envault.env_sync import load_into_env, export_from_env, SyncError


class _FakeVault:
    def __init__(self, data: dict):
        self._data = dict(data)
        self._saved = False

    def keys(self):
        return list(self._data.keys())

    def has(self, key):
        return key in self._data

    def get(self, key):
        return self._data[key]

    def set(self, key, value):
        self._data[key] = value

    def save(self):
        self._saved = True


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure test env vars don't bleed between tests."""
    for key in ("FOO", "BAR", "BAZ"):
        monkeypatch.delenv(key, raising=False)
    yield


def test_load_into_env_sets_variables(monkeypatch):
    vault = _FakeVault({"FOO": "hello", "BAR": "world"})
    result = load_into_env(vault)
    assert os.environ["FOO"] == "hello"
    assert os.environ["BAR"] == "world"
    assert set(result.loaded) == {"FOO", "BAR"}
    assert result.skipped == []


def test_load_into_env_skips_existing_by_default(monkeypatch):
    monkeypatch.setenv("FOO", "original")
    vault = _FakeVault({"FOO": "new_value"})
    result = load_into_env(vault)
    assert os.environ["FOO"] == "original"
    assert "FOO" in result.skipped
    assert result.loaded == []


def test_load_into_env_overwrites_when_flag_set(monkeypatch):
    monkeypatch.setenv("FOO", "original")
    vault = _FakeVault({"FOO": "new_value"})
    result = load_into_env(vault, overwrite=True)
    assert os.environ["FOO"] == "new_value"
    assert "FOO" in result.loaded


def test_load_specific_keys_only(monkeypatch):
    vault = _FakeVault({"FOO": "a", "BAR": "b", "BAZ": "c"})
    result = load_into_env(vault, keys=["FOO", "BAZ"])
    assert os.environ["FOO"] == "a"
    assert os.environ["BAZ"] == "c"
    assert "BAR" not in os.environ
    assert set(result.loaded) == {"FOO", "BAZ"}


def test_load_missing_key_raises():
    vault = _FakeVault({"FOO": "a"})
    with pytest.raises(SyncError, match="BAR"):
        load_into_env(vault, keys=["BAR"])


def test_export_from_env_writes_to_vault(monkeypatch):
    monkeypatch.setenv("FOO", "from_env")
    vault = _FakeVault({})
    result = export_from_env(vault, keys=["FOO"])
    assert vault.get("FOO") == "from_env"
    assert "FOO" in result.exported


def test_export_from_env_skips_existing_by_default(monkeypatch):
    monkeypatch.setenv("FOO", "env_val")
    vault = _FakeVault({"FOO": "vault_val"})
    result = export_from_env(vault, keys=["FOO"])
    assert vault.get("FOO") == "vault_val"
    assert "FOO" in result.skipped


def test_export_from_env_overwrites_when_flag_set(monkeypatch):
    monkeypatch.setenv("FOO", "env_val")
    vault = _FakeVault({"FOO": "vault_val"})
    result = export_from_env(vault, keys=["FOO"], overwrite=True)
    assert vault.get("FOO") == "env_val"
    assert "FOO" in result.exported


def test_export_missing_env_var_raises(monkeypatch):
    monkeypatch.delenv("MISSING_KEY", raising=False)
    vault = _FakeVault({})
    with pytest.raises(SyncError, match="MISSING_KEY"):
        export_from_env(vault, keys=["MISSING_KEY"])


def test_sync_result_summary():
    from envault.env_sync import SyncResult
    r = SyncResult(loaded=["A", "B"], skipped=["C"], exported=[])
    assert "2" in r.summary()
    assert "1" in r.summary()
