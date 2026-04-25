"""Tests for envault.env_clone."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from envault.env_clone import clone_vault, CloneError, CloneResult


PASSWORD = "secret"


class _FakeVault:
    def __init__(self, name: str, data: dict | None = None):
        self.name = name
        self._data: dict[str, str] = data or {}
        self.saved = False

    def keys(self):
        return list(self._data.keys())

    def has(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str) -> str:
        return self._data[key]

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def save(self) -> None:
        self.saved = True


def _patch_vaults(src_vault: _FakeVault, dst_vault: _FakeVault | None, dst_exists: bool):
    """Return a context-manager stack that patches storage and Vault calls."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("envault.env_clone.vault_exists", side_effect=lambda n: n == src_vault.name or dst_exists), \
             patch("envault.env_clone.Vault") as MockVault:
            MockVault.open.side_effect = lambda name, pw: src_vault if name == src_vault.name else dst_vault
            MockVault.create.return_value = dst_vault
            yield MockVault

    return _ctx()


def test_clone_all_keys():
    src = _FakeVault("src", {"A": "1", "B": "2"})
    dst = _FakeVault("dst")

    with _patch_vaults(src, dst, dst_exists=False):
        result = clone_vault("src", PASSWORD, "dst", PASSWORD)

    assert set(result.copied) == {"A", "B"}
    assert result.skipped == []
    assert dst._data == {"A": "1", "B": "2"}
    assert dst.saved


def test_clone_with_pattern():
    src = _FakeVault("src", {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_KEY": "xyz"})
    dst = _FakeVault("dst")

    with _patch_vaults(src, dst, dst_exists=False):
        result = clone_vault("src", PASSWORD, "dst", PASSWORD, pattern="DB_*")

    assert set(result.copied) == {"DB_HOST", "DB_PORT"}
    assert "APP_KEY" in result.skipped


def test_clone_skip_existing_without_overwrite():
    src = _FakeVault("src", {"KEY": "new_value"})
    dst = _FakeVault("dst", {"KEY": "old_value"})

    with _patch_vaults(src, dst, dst_exists=True):
        result = clone_vault("src", PASSWORD, "dst", PASSWORD, overwrite=False)

    assert "KEY" in result.skipped
    assert dst._data["KEY"] == "old_value"


def test_clone_overwrite_existing():
    src = _FakeVault("src", {"KEY": "new_value"})
    dst = _FakeVault("dst", {"KEY": "old_value"})

    with _patch_vaults(src, dst, dst_exists=True):
        result = clone_vault("src", PASSWORD, "dst", PASSWORD, overwrite=True)

    assert "KEY" in result.copied
    assert dst._data["KEY"] == "new_value"


def test_clone_source_not_found_raises():
    with patch("envault.env_clone.vault_exists", return_value=False):
        with pytest.raises(CloneError, match="does not exist"):
            clone_vault("missing", PASSWORD, "dst", PASSWORD)


def test_clone_result_summary():
    r = CloneResult(source="a", destination="b", copied=["X", "Y"], skipped=["Z"])
    summary = r.summary()
    assert "2" in summary
    assert "1" in summary
    assert "a" in summary
    assert "b" in summary
