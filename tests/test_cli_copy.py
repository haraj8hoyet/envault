"""Tests for envault/cli_copy.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_copy import copy_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def patch_vault_dir(tmp_path):
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        yield tmp_path


def _create_vault(name, password, data, tmp_path):
    from envault.vault import Vault
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        v = Vault.create(name, password)
        for k, val in data.items():
            v.set(k, val)


def test_copy_var_command(runner, patch_vault_dir):
    _create_vault("src", "pass1", {"KEY": "val"}, patch_vault_dir)
    _create_vault("dst", "pass2", {}, patch_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(patch_vault_dir)):
        with patch("envault.cli_copy.vault_exists", return_value=True):
            result = runner.invoke(copy_cli, ["var", "src", "dst", "KEY",
                                              "--src-password", "pass1",
                                              "--dst-password", "pass2"])
    assert result.exit_code == 0
    assert "Copied 'KEY'" in result.output


def test_copy_var_vault_not_found(runner, patch_vault_dir):
    with patch("envault.cli_copy.vault_exists", return_value=False):
        result = runner.invoke(copy_cli, ["var", "src", "dst", "KEY",
                                          "--src-password", "p",
                                          "--dst-password", "p"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_copy_all_command(runner, patch_vault_dir):
    _create_vault("src", "pass1", {"A": "1", "B": "2"}, patch_vault_dir)
    _create_vault("dst", "pass2", {}, patch_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(patch_vault_dir)):
        with patch("envault.cli_copy.vault_exists", return_value=True):
            result = runner.invoke(copy_cli, ["all", "src", "dst",
                                              "--src-password", "pass1",
                                              "--dst-password", "pass2"])
    assert result.exit_code == 0
    assert "Copied" in result.output


def test_copy_all_no_overwrite_flag(runner, patch_vault_dir):
    _create_vault("src", "pass1", {"A": "new"}, patch_vault_dir)
    _create_vault("dst", "pass2", {"A": "old"}, patch_vault_dir)
    with patch("envault.storage.VAULT_DIR", str(patch_vault_dir)):
        with patch("envault.cli_copy.vault_exists", return_value=True):
            result = runner.invoke(copy_cli, ["all", "src", "dst",
                                              "--src-password", "pass1",
                                              "--dst-password", "pass2",
                                              "--no-overwrite"])
    assert result.exit_code == 0
    assert "skipped" in result.output
