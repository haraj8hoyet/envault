"""Tests for the envault CLI."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli import cli


PASSWORD = "testpassword"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def patch_vault_dir(tmp_path):
    with patch("envault.storage.VAULT_DIR", tmp_path):
        yield


def test_create_vault(runner):
    result = runner.invoke(cli, ["create", "myapp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    assert result.exit_code == 0
    assert "created successfully" in result.output


def test_create_duplicate_vault(runner):
    runner.invoke(cli, ["create", "myapp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    result = runner.invoke(cli, ["create", "myapp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_set_and_get(runner):
    runner.invoke(cli, ["create", "myapp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    result = runner.invoke(cli, ["set", "myapp", "DB_URL", "postgres://localhost"], input=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "Set 'DB_URL'" in result.output

    result = runner.invoke(cli, ["get", "myapp", "DB_URL"], input=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "postgres://localhost" in result.output


def test_get_missing_key(runner):
    runner.invoke(cli, ["create", "myapp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    result = runner.invoke(cli, ["get", "myapp", "MISSING"], input=f"{PASSWORD}\n")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_list_empty_vault(runner):
    runner.invoke(cli, ["create", "myapp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    result = runner.invoke(cli, ["list", "myapp"], input=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "no variables" in result.output


def test_export(runner):
    runner.invoke(cli, ["create", "myapp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    runner.invoke(cli, ["set", "myapp", "API_KEY", "secret"], input=f"{PASSWORD}\n")
    result = runner.invoke(cli, ["export", "myapp"], input=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "export API_KEY=" in result.output
    assert "secret" in result.output
