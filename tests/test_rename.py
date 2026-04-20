"""Tests for envault.rename module."""

import pytest
from unittest.mock import patch

from envault.vault import Vault
from envault.rename import rename_key, rename_keys_bulk, RenameError


@pytest.fixture
def tmp_vault_dir(tmp_path):
    with patch("envault.storage.VAULT_DIR", tmp_path):
        yield tmp_path


def _make_vault(name: str, password: str, data: dict) -> None:
    v = Vault.create(name, password)
    for k, val in data.items():
        v.set(k, val)
    v.save(password)


# ---------------------------------------------------------------------------
# rename_key
# ---------------------------------------------------------------------------

def test_rename_key_basic(tmp_vault_dir):
    _make_vault("myapp", "secret", {"OLD_KEY": "value123"})
    rename_key("myapp", "OLD_KEY", "NEW_KEY", "secret")
    v = Vault.open("myapp", "secret")
    assert v.get("NEW_KEY") == "value123"
    assert not v.has("OLD_KEY")


def test_rename_key_preserves_other_keys(tmp_vault_dir):
    _make_vault("myapp", "secret", {"A": "1", "B": "2"})
    rename_key("myapp", "A", "ALPHA", "secret")
    v = Vault.open("myapp", "secret")
    assert v.get("ALPHA") == "1"
    assert v.get("B") == "2"
    assert not v.has("A")


def test_rename_key_missing_old_key_raises(tmp_vault_dir):
    _make_vault("myapp", "secret", {"EXISTING": "val"})
    with pytest.raises(RenameError, match="MISSING"):
        rename_key("myapp", "MISSING", "OTHER", "secret")


def test_rename_key_new_key_exists_no_overwrite_raises(tmp_vault_dir):
    _make_vault("myapp", "secret", {"FOO": "foo_val", "BAR": "bar_val"})
    with pytest.raises(RenameError, match="already exists"):
        rename_key("myapp", "FOO", "BAR", "secret", overwrite=False)


def test_rename_key_new_key_exists_with_overwrite(tmp_vault_dir):
    _make_vault("myapp", "secret", {"FOO": "new_val", "BAR": "old_val"})
    rename_key("myapp", "FOO", "BAR", "secret", overwrite=True)
    v = Vault.open("myapp", "secret")
    assert v.get("BAR") == "new_val"
    assert not v.has("FOO")


def test_rename_key_nonexistent_vault_raises(tmp_vault_dir):
    with pytest.raises(RenameError, match="does not exist"):
        rename_key("ghost", "K", "V", "secret")


# ---------------------------------------------------------------------------
# rename_keys_bulk
# ---------------------------------------------------------------------------

def test_rename_keys_bulk_success(tmp_vault_dir):
    _make_vault("myapp", "secret", {"A": "1", "B": "2", "C": "3"})
    result = rename_keys_bulk("myapp", {"A": "ALPHA", "B": "BETA"}, "secret")
    assert result == {"A": "ALPHA", "B": "BETA"}
    v = Vault.open("myapp", "secret")
    assert v.get("ALPHA") == "1"
    assert v.get("BETA") == "2"
    assert v.get("C") == "3"


def test_rename_keys_bulk_partial_failure_raises(tmp_vault_dir):
    _make_vault("myapp", "secret", {"A": "1"})
    with pytest.raises(RenameError, match="could not be renamed"):
        rename_keys_bulk("myapp", {"A": "ALPHA", "MISSING": "X"}, "secret")


def test_rename_keys_bulk_nonexistent_vault_raises(tmp_vault_dir):
    with pytest.raises(RenameError, match="does not exist"):
        rename_keys_bulk("ghost", {"A": "B"}, "secret")
