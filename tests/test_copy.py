"""Tests for envault/copy.py"""

import pytest
from unittest.mock import patch
from envault.vault import Vault
from envault.copy import copy_variable, copy_all, copy_variables, CopyError


TEST_DIR = "/tmp/envault_copy_tests"


@pytest.fixture
def tmp_vault_dir(tmp_path):
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        yield tmp_path


def _make_vault(name, password, data, tmp_path):
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        v = Vault.create(name, password)
        for k, val in data.items():
            v.set(k, val)
    return v


def test_copy_variable(tmp_vault_dir):
    _make_vault("src", "pass1", {"FOO": "bar"}, tmp_vault_dir)
    _make_vault("dst", "pass2", {}, tmp_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(tmp_vault_dir)):
        key = copy_variable("src", "pass1", "dst", "pass2", "FOO")
        assert key == "FOO"
        dst = Vault.open("dst", "pass2")
        assert dst.get("FOO") == "bar"


def test_copy_variable_with_rename(tmp_vault_dir):
    _make_vault("src", "pass1", {"FOO": "bar"}, tmp_vault_dir)
    _make_vault("dst", "pass2", {}, tmp_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(tmp_vault_dir)):
        key = copy_variable("src", "pass1", "dst", "pass2", "FOO", new_key="BAR")
        assert key == "BAR"
        dst = Vault.open("dst", "pass2")
        assert dst.get("BAR") == "bar"
        assert dst.get("FOO") is None


def test_copy_variable_missing_key(tmp_vault_dir):
    _make_vault("src", "pass1", {}, tmp_vault_dir)
    _make_vault("dst", "pass2", {}, tmp_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(tmp_vault_dir)):
        with pytest.raises(CopyError):
            copy_variable("src", "pass1", "dst", "pass2", "MISSING")


def test_copy_all(tmp_vault_dir):
    _make_vault("src", "pass1", {"A": "1", "B": "2"}, tmp_vault_dir)
    _make_vault("dst", "pass2", {}, tmp_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(tmp_vault_dir)):
        results = copy_all("src", "pass1", "dst", "pass2")
        assert results["A"] == "copied"
        assert results["B"] == "copied"
        dst = Vault.open("dst", "pass2")
        assert dst.get("A") == "1"
        assert dst.get("B") == "2"


def test_copy_all_no_overwrite(tmp_vault_dir):
    _make_vault("src", "pass1", {"A": "new"}, tmp_vault_dir)
    _make_vault("dst", "pass2", {"A": "old"}, tmp_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(tmp_vault_dir)):
        results = copy_all("src", "pass1", "dst", "pass2", overwrite=False)
        assert results["A"] == "skipped"
        dst = Vault.open("dst", "pass2")
        assert dst.get("A") == "old"
