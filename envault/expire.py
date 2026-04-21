"""Bulk expiration utilities: find and purge expired keys across a vault."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Tuple

from envault.vault import Vault
from envault.ttl import is_expired


class ExpireError(Exception):
    """Raised when an expiration operation fails."""


def find_expired(vault: Vault) -> List[str]:
    """Return a list of keys whose TTL has passed."""
    expired = []
    for key in vault.keys():
        try:
            if is_expired(vault, key):
                expired.append(key)
        except Exception:
            # Key has no TTL metadata — skip it
            pass
    return sorted(expired)


def find_expiring_soon(vault: Vault, within_seconds: int = 3600) -> List[Tuple[str, datetime]]:
    """Return keys that will expire within *within_seconds* seconds.

    Returns a list of (key, expires_at) tuples sorted by expiry time.
    """
    now = datetime.now(tz=timezone.utc)
    results: List[Tuple[str, datetime]] = []
    for key in vault.keys():
        meta = vault.get_meta(key) if hasattr(vault, "get_meta") else {}
        expires_raw = meta.get("expires_at") if meta else None
        if not expires_raw:
            continue
        try:
            expires_at = datetime.fromisoformat(expires_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            delta = (expires_at - now).total_seconds()
            if 0 < delta <= within_seconds:
                results.append((key, expires_at))
        except (ValueError, TypeError):
            continue
    return sorted(results, key=lambda t: t[1])


def purge_expired(vault: Vault) -> List[str]:
    """Delete all expired keys from *vault*. Returns the list of removed keys."""
    keys = find_expired(vault)
    for key in keys:
        vault.delete(key)
    return keys
