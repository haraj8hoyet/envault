"""Vault locking: prevent concurrent access to a vault by writing a lock file."""

import os
import time
import json
from pathlib import Path
from envault.storage import _vault_path


class LockError(Exception):
    """Raised when a vault cannot be locked or is already locked."""


def _lock_path(vault_name: str) -> Path:
    return _vault_path(vault_name).with_suffix(".lock")


def acquire_lock(vault_name: str, timeout: float = 5.0, poll: float = 0.1) -> None:
    """Acquire an exclusive lock on *vault_name*.

    Tries for up to *timeout* seconds, polling every *poll* seconds.
    Raises LockError if the lock cannot be acquired in time.
    """
    lock_file = _lock_path(vault_name)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            info = {"pid": os.getpid(), "acquired_at": time.time()}
            os.write(fd, json.dumps(info).encode())
            os.close(fd)
            return
        except FileExistsError:
            time.sleep(poll)
    # One last attempt to read who holds the lock
    try:
        info = json.loads(lock_file.read_text())
        holder = info.get("pid", "unknown")
    except Exception:
        holder = "unknown"
    raise LockError(
        f"Vault '{vault_name}' is locked by PID {holder}. "
        "Try again or remove the lock file manually."
    )


def release_lock(vault_name: str) -> None:
    """Release the lock on *vault_name*. Safe to call even if not locked."""
    lock_file = _lock_path(vault_name)
    try:
        lock_file.unlink()
    except FileNotFoundError:
        pass


def is_locked(vault_name: str) -> bool:
    """Return True if a lock file exists for *vault_name*."""
    return _lock_path(vault_name).exists()


def lock_info(vault_name: str) -> dict | None:
    """Return lock metadata dict or None if the vault is not locked."""
    lock_file = _lock_path(vault_name)
    if not lock_file.exists():
        return None
    try:
        return json.loads(lock_file.read_text())
    except Exception:
        return {}
