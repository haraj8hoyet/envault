"""Tests for envault.rotate."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
import os

from envault.vault import Vault
from envault.rotate import rotate_password, verify_password, RotationError


@pytest.fixture()
def tmp_vault_dir(tmp_path):
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        yield tmp_path


def _make_vault(name, password, variables):
    v = Vault.create(name, password)
    for k, val in variables.items():
        v.set(k, val)
    v.save()
    return v


def test_rotate_changes_password(tmp_vault_dir):
    _make_vault("myvault", "old-pass", {"KEY": "value", "FOO": "bar"})

    count = rotate_password("myvault", "old-pass", "new-pass")
    assert count == 2

    # old password should no longer work
    assert not verify_password("myvault", "old-pass")
    # new password should work
    assert verify_password("myvault", "new-pass")


def test_rotate_preserves_data(tmp_vault_dir):
    _make_vault("myvault", "old-pass", {"API_KEY": "secret123"})
    rotate_password("myvault", "old-pass", "new-pass")

    v = Vault.open("myvault", "new-pass")
    assert v.get("API_KEY") == "secret123"


def test_rotate_nonexistent_vault(tmp_vault_dir):
    with pytest.raises(RotationError, match="does not exist"):
        rotate_password("ghost", "x", "y")


def test_rotate_wrong_old_password(tmp_vault_dir):
    _make_vault("myvault", "correct", {"X": "1"})
    with pytest.raises(RotationError, match="old password"):
        rotate_password("myvault", "wrong", "new-pass")


def test_verify_password_correct(tmp_vault_dir):
    _make_vault("myvault", "mypass", {})
    assert verify_password("myvault", "mypass") is True


def test_verify_password_wrong(tmp_vault_dir):
    _make_vault("myvault", "mypass", {})
    assert verify_password("myvault", "wrongpass") is False


def test_verify_password_missing_vault(tmp_vault_dir):
    assert verify_password("no-such-vault", "pass") is False
