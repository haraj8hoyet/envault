"""Tests for envault.expire — bulk expiration helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from envault.expire import find_expired, find_expiring_soon, purge_expired


def _utc_iso(delta_seconds: int) -> str:
    dt = datetime.now(tz=timezone.utc) + timedelta(seconds=delta_seconds)
    return dt.isoformat()


def _make_vault(key_meta: dict) -> MagicMock:
    """Build a fake Vault whose keys/get_meta match *key_meta*."""
    vault = MagicMock()
    vault.keys.return_value = list(key_meta.keys())

    def _get_meta(key):
        return key_meta.get(key, {})

    vault.get_meta.side_effect = _get_meta
    return vault


# ---------------------------------------------------------------------------
# find_expired
# ---------------------------------------------------------------------------

def test_find_expired_returns_past_keys():
    from unittest.mock import patch

    vault = _make_vault({
        "OLD_KEY": {"expires_at": _utc_iso(-10)},
        "FRESH_KEY": {"expires_at": _utc_iso(9999)},
        "NO_TTL": {},
    })

    with patch("envault.expire.is_expired", side_effect=lambda v, k: k == "OLD_KEY"):
        result = find_expired(vault)

    assert result == ["OLD_KEY"]


def test_find_expired_empty_when_none_expired():
    from unittest.mock import patch

    vault = _make_vault({"A": {"expires_at": _utc_iso(500)}})

    with patch("envault.expire.is_expired", return_value=False):
        result = find_expired(vault)

    assert result == []


def test_find_expired_skips_exception():
    from unittest.mock import patch

    vault = _make_vault({"BAD": {}})

    with patch("envault.expire.is_expired", side_effect=Exception("no ttl")):
        result = find_expired(vault)

    assert result == []


# ---------------------------------------------------------------------------
# find_expiring_soon
# ---------------------------------------------------------------------------

def test_find_expiring_soon_includes_near_keys():
    vault = _make_vault({
        "SOON": {"expires_at": _utc_iso(300)},
        "LATER": {"expires_at": _utc_iso(7200)},
        "PAST": {"expires_at": _utc_iso(-1)},
        "NO_TTL": {},
    })
    result = find_expiring_soon(vault, within_seconds=3600)
    keys = [k for k, _ in result]
    assert "SOON" in keys
    assert "LATER" not in keys
    assert "PAST" not in keys


def test_find_expiring_soon_sorted_by_expiry():
    vault = _make_vault({
        "B": {"expires_at": _utc_iso(600)},
        "A": {"expires_at": _utc_iso(200)},
    })
    result = find_expiring_soon(vault, within_seconds=3600)
    assert [k for k, _ in result] == ["A", "B"]


# ---------------------------------------------------------------------------
# purge_expired
# ---------------------------------------------------------------------------

def test_purge_expired_deletes_and_returns_keys():
    from unittest.mock import patch

    vault = _make_vault({
        "STALE": {"expires_at": _utc_iso(-5)},
        "ALIVE": {"expires_at": _utc_iso(999)},
    })

    with patch("envault.expire.is_expired", side_effect=lambda v, k: k == "STALE"):
        removed = purge_expired(vault)

    assert removed == ["STALE"]
    vault.delete.assert_called_once_with("STALE")


def test_purge_expired_nothing_to_remove():
    from unittest.mock import patch

    vault = _make_vault({"KEY": {"expires_at": _utc_iso(100)}})

    with patch("envault.expire.is_expired", return_value=False):
        removed = purge_expired(vault)

    assert removed == []
    vault.delete.assert_not_called()
