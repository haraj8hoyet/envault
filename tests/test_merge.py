"""Tests for envault.merge."""

from __future__ import annotations

import os
import pytest

from envault.merge import MergeError, MergeResult, MergeStrategy, merge_dicts, merge_vaults
from envault.vault import Vault


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    import envault.storage as storage
    monkeypatch.setattr(storage, "_vault_path", lambda name: tmp_path / f"{name}.vault")
    return tmp_path


def _make_vault(name: str, password: str, data: dict) -> Vault:
    v = Vault.create(name, password)
    for k, val in data.items():
        v.set(k, val)
    return v


# ---------------------------------------------------------------------------
# merge_dicts tests
# ---------------------------------------------------------------------------

def test_merge_dicts_adds_new_keys():
    src = {"A": "1", "B": "2"}
    dst = {"C": "3"}
    merged, result = merge_dicts(src, dst)
    assert merged["A"] == "1"
    assert merged["B"] == "2"
    assert merged["C"] == "3"
    assert set(result.added) == {"A", "B"}


def test_merge_dicts_skip_strategy_keeps_destination():
    src = {"KEY": "new"}
    dst = {"KEY": "old"}
    merged, result = merge_dicts(src, dst, strategy=MergeStrategy.SKIP)
    assert merged["KEY"] == "old"
    assert "KEY" in result.skipped


def test_merge_dicts_overwrite_strategy_replaces_value():
    src = {"KEY": "new"}
    dst = {"KEY": "old"}
    merged, result = merge_dicts(src, dst, strategy=MergeStrategy.OVERWRITE)
    assert merged["KEY"] == "new"
    assert "KEY" in result.overwritten


def test_merge_dicts_empty_src():
    merged, result = merge_dicts({}, {"X": "1"})
    assert merged == {"X": "1"}
    assert result.summary() == "no changes"


# ---------------------------------------------------------------------------
# merge_vaults tests
# ---------------------------------------------------------------------------

def test_merge_vaults_adds_missing_keys(tmp_vault_dir):
    src = _make_vault("src", "pass", {"FOO": "bar", "BAZ": "qux"})
    dst = _make_vault("dst", "pass", {})
    result = merge_vaults(src, dst)
    assert dst.get("FOO") == "bar"
    assert dst.get("BAZ") == "qux"
    assert set(result.added) == {"FOO", "BAZ"}


def test_merge_vaults_skip_does_not_overwrite(tmp_vault_dir):
    src = _make_vault("src2", "pass", {"KEY": "from_src"})
    dst = _make_vault("dst2", "pass", {"KEY": "original"})
    result = merge_vaults(src, dst, strategy=MergeStrategy.SKIP)
    assert dst.get("KEY") == "original"
    assert "KEY" in result.skipped


def test_merge_vaults_overwrite_replaces_value(tmp_vault_dir):
    src = _make_vault("src3", "pass", {"KEY": "new_val"})
    dst = _make_vault("dst3", "pass", {"KEY": "old_val"})
    result = merge_vaults(src, dst, strategy=MergeStrategy.OVERWRITE)
    assert dst.get("KEY") == "new_val"
    assert "KEY" in result.overwritten


def test_merge_vaults_subset_of_keys(tmp_vault_dir):
    src = _make_vault("src4", "pass", {"A": "1", "B": "2", "C": "3"})
    dst = _make_vault("dst4", "pass", {})
    result = merge_vaults(src, dst, keys=["A", "C"])
    assert dst.get("A") == "1"
    assert dst.get("C") == "3"
    assert not dst.has("B")
    assert set(result.added) == {"A", "C"}


def test_merge_vaults_missing_key_raises(tmp_vault_dir):
    src = _make_vault("src5", "pass", {"X": "1"})
    dst = _make_vault("dst5", "pass", {})
    with pytest.raises(MergeError, match="MISSING"):
        merge_vaults(src, dst, keys=["MISSING"])


def test_merge_result_summary_format():
    r = MergeResult()
    r.added = ["A"]
    r.overwritten = ["B"]
    r.skipped = ["C", "D"]
    summary = r.summary()
    assert "added=1" in summary
    assert "overwritten=1" in summary
    assert "skipped=2" in summary
