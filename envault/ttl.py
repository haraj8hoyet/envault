"""TTL (time-to-live) support for vault variables."""

import time
from typing import Optional

TTL_META_KEY = "_ttl"
EXPIRED_AT_META_KEY = "_expires_at"


class TTLError(Exception):
    pass


def set_ttl(vault, key: str, seconds: int) -> None:
    """Set a TTL on an existing key. Raises TTLError if key not found."""
    if not vault.has(key):
        raise TTLError(f"Key '{key}' not found in vault.")
    if seconds <= 0:
        raise TTLError("TTL must be a positive integer (seconds).")
    expires_at = time.time() + seconds
    meta = vault.get_meta(key) or {}
    meta[TTL_META_KEY] = seconds
    meta[EXPIRED_AT_META_KEY] = expires_at
    vault.set_meta(key, meta)


def get_ttl(vault, key: str) -> Optional[float]:
    """Return remaining TTL in seconds, or None if no TTL is set."""
    meta = vault.get_meta(key) or {}
    expires_at = meta.get(EXPIRED_AT_META_KEY)
    if expires_at is None:
        return None
    remaining = expires_at - time.time()
    return max(remaining, 0.0)


def is_expired(vault, key: str) -> bool:
    """Return True if the key has a TTL and it has expired."""
    remaining = get_ttl(vault, key)
    if remaining is None:
        return False
    return remaining <= 0.0


def clear_ttl(vault, key: str) -> None:
    """Remove TTL from a key. Raises TTLError if key not found."""
    if not vault.has(key):
        raise TTLError(f"Key '{key}' not found in vault.")
    meta = vault.get_meta(key) or {}
    meta.pop(TTL_META_KEY, None)
    meta.pop(EXPIRED_AT_META_KEY, None)
    vault.set_meta(key, meta)


def purge_expired(vault) -> list:
    """Delete all expired keys from vault. Returns list of purged key names."""
    purged = []
    for key in list(vault.keys()):
        if is_expired(vault, key):
            vault.delete(key)
            purged.append(key)
    return purged
