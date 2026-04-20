"""Tests for envault/ttl.py"""

import time
import pytest
from unittest.mock import MagicMock
from envault.ttl import set_ttl, get_ttl, is_expired, clear_ttl, purge_expired, TTLError


def _make_vault(data=None, meta=None):
    """Build a minimal mock vault."""
    store = dict(data or {})
    meta_store = dict(meta or {})
    v = MagicMock()
    v.has.side_effect = lambda k: k in store
    v.keys.side_effect = lambda: list(store.keys())
    v.get_meta.side_effect = lambda k: dict(meta_store.get(k, {}))
    def _set_meta(k, m):
        meta_store[k] = m
    v.set_meta.side_effect = _set_meta
    def _delete(k):
        store.pop(k, None)
    v.delete.side_effect = _delete
    return v


def test_set_ttl_stores_expires_at():
    vault = _make_vault({"KEY": "val"})
    before = time.time()
    set_ttl(vault, "KEY", 60)
    meta = vault.get_meta("KEY")
    assert "_expires_at" in meta
    assert meta["_expires_at"] >= before + 59


def test_set_ttl_missing_key_raises():
    vault = _make_vault()
    with pytest.raises(TTLError, match="not found"):
        set_ttl(vault, "MISSING", 30)


def test_set_ttl_non_positive_raises():
    vault = _make_vault({"K": "v"})
    with pytest.raises(TTLError, match="positive"):
        set_ttl(vault, "K", 0)
    with pytest.raises(TTLError):
        set_ttl(vault, "K", -5)


def test_get_ttl_no_ttl_returns_none():
    vault = _make_vault({"K": "v"})
    assert get_ttl(vault, "K") is None


def test_get_ttl_returns_remaining():
    vault = _make_vault({"K": "v"})
    set_ttl(vault, "K", 100)
    remaining = get_ttl(vault, "K")
    assert 98 < remaining <= 100


def test_is_expired_false_for_future():
    vault = _make_vault({"K": "v"})
    set_ttl(vault, "K", 100)
    assert is_expired(vault, "K") is False


def test_is_expired_true_for_past():
    vault = _make_vault({"K": "v"})
    set_ttl(vault, "K", 1)
    vault.get_meta.side_effect = lambda k: {"_ttl": 1, "_expires_at": time.time() - 1}
    assert is_expired(vault, "K") is True


def test_is_expired_false_when_no_ttl():
    vault = _make_vault({"K": "v"})
    assert is_expired(vault, "K") is False


def test_clear_ttl_removes_meta():
    vault = _make_vault({"K": "v"})
    set_ttl(vault, "K", 60)
    clear_ttl(vault, "K")
    meta = vault.get_meta("K")
    assert "_expires_at" not in meta
    assert "_ttl" not in meta


def test_clear_ttl_missing_key_raises():
    vault = _make_vault()
    with pytest.raises(TTLError):
        clear_ttl(vault, "NOPE")


def test_purge_expired_removes_expired_keys():
    vault = _make_vault({"A": "1", "B": "2", "C": "3"})
    expired_meta = {"_ttl": 1, "_expires_at": time.time() - 10}
    active_meta = {"_ttl": 100, "_expires_at": time.time() + 100}
    def _get_meta(k):
        if k == "A":
            return dict(expired_meta)
        if k == "B":
            return dict(active_meta)
        return {}
    vault.get_meta.side_effect = _get_meta
    purged = purge_expired(vault)
    assert "A" in purged
    assert "B" not in purged
    assert "C" not in purged
    vault.delete.assert_called_once_with("A")
