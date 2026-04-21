"""Tests for envault.alias."""

import pytest

from envault.alias import (
    AliasError,
    clear_aliases,
    list_aliases,
    remove_alias,
    resolve_alias,
    set_alias,
    _alias_file,
)


@pytest.fixture()
def vault_name(tmp_path, monkeypatch):
    """Patch _vault_path so alias files land in tmp_path."""
    import envault.alias as alias_mod
    import envault.storage as storage_mod

    def fake_vault_path(name):
        p = tmp_path / f"{name}.vault"
        return p

    monkeypatch.setattr(storage_mod, "_vault_path", fake_vault_path)
    monkeypatch.setattr(alias_mod, "_vault_path", fake_vault_path)
    return "myvault"


def test_set_and_resolve_alias(vault_name):
    set_alias(vault_name, "db", "DATABASE_URL")
    assert resolve_alias(vault_name, "db") == "DATABASE_URL"


def test_resolve_missing_alias_returns_none(vault_name):
    assert resolve_alias(vault_name, "nonexistent") is None


def test_set_alias_overwrites_existing(vault_name):
    set_alias(vault_name, "db", "DATABASE_URL")
    set_alias(vault_name, "db", "POSTGRES_DSN")
    assert resolve_alias(vault_name, "db") == "POSTGRES_DSN"


def test_set_alias_empty_name_raises(vault_name):
    with pytest.raises(AliasError, match="Alias name"):
        set_alias(vault_name, "", "DATABASE_URL")


def test_set_alias_empty_key_raises(vault_name):
    with pytest.raises(AliasError, match="Target key"):
        set_alias(vault_name, "db", "")


def test_remove_alias(vault_name):
    set_alias(vault_name, "db", "DATABASE_URL")
    remove_alias(vault_name, "db")
    assert resolve_alias(vault_name, "db") is None


def test_remove_nonexistent_alias_raises(vault_name):
    with pytest.raises(AliasError, match="does not exist"):
        remove_alias(vault_name, "ghost")


def test_list_aliases_sorted(vault_name):
    set_alias(vault_name, "redis", "REDIS_URL")
    set_alias(vault_name, "db", "DATABASE_URL")
    result = list_aliases(vault_name)
    assert result == [
        {"alias": "db", "key": "DATABASE_URL"},
        {"alias": "redis", "key": "REDIS_URL"},
    ]


def test_list_aliases_empty(vault_name):
    assert list_aliases(vault_name) == []


def test_clear_aliases_returns_count(vault_name):
    set_alias(vault_name, "a", "A_KEY")
    set_alias(vault_name, "b", "B_KEY")
    count = clear_aliases(vault_name)
    assert count == 2
    assert list_aliases(vault_name) == []


def test_clear_aliases_when_empty(vault_name):
    assert clear_aliases(vault_name) == 0
