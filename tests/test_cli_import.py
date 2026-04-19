"""Tests for CLI import commands."""

import json
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_import import import_cli


TEST_VAULT_DIR = "/tmp/envault_test_import"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def patch_vault_dir(tmp_path):
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        yield tmp_path


def _create_vault(tmp_path, name="myvault", password="secret"):
    from envault.vault import Vault
    with patch("envault.storage.VAULT_DIR", str(tmp_path)):
        Vault.create(name, password)


def test_import_file_dotenv(runner, patch_vault_dir, tmp_path):
    _create_vault(patch_vault_dir)
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux")

    result = runner.invoke(
        import_cli, ["file", "myvault", str(env_file), "--password", "secret"]
    )
    assert result.exit_code == 0
    assert "Imported 2" in result.output


def test_import_file_json(runner, patch_vault_dir, tmp_path):
    _create_vault(patch_vault_dir)
    json_file = tmp_path / "vars.json"
    json_file.write_text(json.dumps({"KEY": "value"}))

    result = runner.invoke(
        import_cli, ["file", "myvault", str(json_file), "--password", "secret"]
    )
    assert result.exit_code == 0
    assert "Imported 1" in result.output


def test_import_file_skips_existing(runner, patch_vault_dir, tmp_path):
    from envault.vault import Vault
    with patch("envault.storage.VAULT_DIR", str(patch_vault_dir)):
        v = Vault.create("skipvault", "pass")
        v.set("FOO", "original")

    env_file = tmp_path / ".env"
    env_file.write_text("FOO=new\nBAR=baz")

    result = runner.invoke(
        import_cli, ["file", "skipvault", str(env_file), "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "skipped 1" in result.output


def test_import_file_overwrite(runner, patch_vault_dir, tmp_path):
    from envault.vault import Vault
    with patch("envault.storage.VAULT_DIR", str(patch_vault_dir)):
        v = Vault.create("overvault", "pass")
        v.set("FOO", "original")

    env_file = tmp_path / ".env"
    env_file.write_text("FOO=new")

    result = runner.invoke(
        import_cli,
        ["file", "overvault", str(env_file), "--password", "pass", "--overwrite"],
    )
    assert result.exit_code == 0
    assert "Imported 1" in result.output


def test_import_env_filtered(runner, patch_vault_dir):
    _create_vault(patch_vault_dir)
    os.environ["_ENVAULT_CLI_TEST"] = "hello"

    result = runner.invoke(
        import_cli,
        ["env", "myvault", "_ENVAULT_CLI_TEST", "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "Imported 1" in result.output
    del os.environ["_ENVAULT_CLI_TEST"]
