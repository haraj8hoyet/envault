"""Tests for Vault high-level operations and encrypted storage."""

import pytest
from pathlib import Path
from envault.vault import Vault
from envault.storage import vault_exists, list_vaults, delete_vault


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path


def test_create_and_open(tmp_vault_dir, monkeypatch):
    monkeypatch.setattr("envault.storage.DEFAULT_VAULT_DIR", tmp_vault_dir)
    v = Vault.create("myapp", "secret")
    assert vault_exists("myapp", tmp_vault_dir)
    v2 = Vault.open("myapp", "secret")
    assert v2.all() == {}


def test_set_and_get(tmp_vault_dir, monkeypatch):
    monkeypatch.setattr("envault.storage.DEFAULT_VAULT_DIR", tmp_vault_dir)
    v = Vault.create("myapp", "secret")
    v.set("DB_URL", "postgres://localhost/db")
    assert v.get("DB_URL") == "postgres://localhost/db"


def test_persistence_across_open(tmp_vault_dir, monkeypatch):
    monkeypatch.setattr("envault.storage.DEFAULT_VAULT_DIR", tmp_vault_dir)
    v = Vault.create("myapp", "secret")
    v.set("API_KEY", "xyz")
    v2 = Vault.open("myapp", "secret")
    assert v2.get("API_KEY") == "xyz"


def test_delete_key(tmp_vault_dir, monkeypatch):
    monkeypatch.setattr("envault.storage.DEFAULT_VAULT_DIR", tmp_vault_dir)
    v = Vault.create("myapp", "secret")
    v.set("TEMP", "value")
    v.delete("TEMP")
    with pytest.raises(KeyError):
        v.get("TEMP")


def test_wrong_password_on_open(tmp_vault_dir, monkeypatch):
    monkeypatch.setattr("envault.storage.DEFAULT_VAULT_DIR", tmp_vault_dir)
    Vault.create("myapp", "correct")
    with pytest.raises(ValueError):
        Vault.open("myapp", "wrong")


def test_list_vaults(tmp_vault_dir, monkeypatch):
    monkeypatch.setattr("envault.storage.DEFAULT_VAULT_DIR", tmp_vault_dir)
    Vault.create("app1", "p")
    Vault.create("app2", "p")
    vaults = list_vaults(tmp_vault_dir)
    assert set(vaults) == {"app1", "app2"}
