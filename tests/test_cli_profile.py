"""Tests for envault/cli_profile.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_profile import profile_cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def patch_profile_dir(tmp_path):
    with patch("envault.profile._profile_path") as mock:
        mock.return_value = tmp_path / "profiles.json"
        yield tmp_path


def test_create_profile_command(runner, patch_profile_dir):
    result = runner.invoke(profile_cli, ["create", "dev", "app", "db"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "app" in result.output


def test_create_duplicate_profile_fails(runner, patch_profile_dir):
    runner.invoke(profile_cli, ["create", "dev", "app"])
    result = runner.invoke(profile_cli, ["create", "dev", "db"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_list_profiles_empty(runner, patch_profile_dir):
    result = runner.invoke(profile_cli, ["list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_list_profiles_shows_names(runner, patch_profile_dir):
    runner.invoke(profile_cli, ["create", "dev", "app"])
    runner.invoke(profile_cli, ["create", "prod", "app"])
    result = runner.invoke(profile_cli, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_show_profile(runner, patch_profile_dir):
    runner.invoke(profile_cli, ["create", "staging", "api", "cache"])
    result = runner.invoke(profile_cli, ["show", "staging"])
    assert result.exit_code == 0
    assert "api" in result.output
    assert "cache" in result.output


def test_show_missing_profile_fails(runner, patch_profile_dir):
    result = runner.invoke(profile_cli, ["show", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_delete_profile_command(runner, patch_profile_dir):
    runner.invoke(profile_cli, ["create", "dev", "app"])
    result = runner.invoke(profile_cli, ["delete", "dev"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_update_profile_command(runner, patch_profile_dir):
    runner.invoke(profile_cli, ["create", "dev", "old"])
    result = runner.invoke(profile_cli, ["update", "dev", "new1", "new2"])
    assert result.exit_code == 0
    assert "updated" in result.output
