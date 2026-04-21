"""Tests for envault.lock — vault locking primitives."""

import json
import os
import time
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.lock import (
    acquire_lock,
    release_lock,
    is_locked,
    lock_info,
    LockError,
    _lock_path,
)


@pytest.fixture()
def tmp_vault_dir(tmp_path, monkeypatch):
    """Redirect vault storage to a temp directory."""
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    # Patch _vault_path so lock files land in tmp_path
    import envault.storage as storage
    monkeypatch.setattr(
        storage,
        "_vault_path",
        lambda name: tmp_path / f"{name}.vault",
    )
    import envault.lock as lock_mod
    monkeypatch.setattr(
        lock_mod,
        "_vault_path",
        lambda name: tmp_path / f"{name}.vault",
    )
    return tmp_path


def test_acquire_and_release(tmp_vault_dir):
    acquire_lock("myvault")
    assert is_locked("myvault")
    release_lock("myvault")
    assert not is_locked("myvault")


def test_lock_info_contains_pid(tmp_vault_dir):
    acquire_lock("myvault")
    info = lock_info("myvault")
    assert info is not None
    assert info["pid"] == os.getpid()
    assert "acquired_at" in info
    release_lock("myvault")


def test_lock_info_returns_none_when_not_locked(tmp_vault_dir):
    assert lock_info("myvault") is None


def test_acquire_raises_when_already_locked(tmp_vault_dir):
    acquire_lock("myvault")
    with pytest.raises(LockError, match="locked"):
        acquire_lock("myvault", timeout=0.2, poll=0.05)
    release_lock("myvault")


def test_release_is_idempotent(tmp_vault_dir):
    """Releasing an unlocked vault should not raise."""
    release_lock("nonexistent")  # must not raise


def test_is_locked_false_before_acquire(tmp_vault_dir):
    assert not is_locked("myvault")


def test_lock_error_message_contains_pid(tmp_vault_dir):
    acquire_lock("myvault")
    lock_file = _lock_path("myvault")
    lock_file.write_text(json.dumps({"pid": 99999, "acquired_at": time.time()}))
    with pytest.raises(LockError, match="99999"):
        acquire_lock("myvault", timeout=0.15, poll=0.05)
    release_lock("myvault")
