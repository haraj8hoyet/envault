"""Tests for envault/cli_tags.py."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envault.cli_tags import tag_cli


@pytest.fixture()
def runner():
    return CliRunner()


def _mock_vault(keys_and_tags=None):
    """Build a MagicMock that behaves like a Vault with tag support."""
    vault = MagicMock()
    meta_store = {}

    def has(key):
        return key in (keys_and_tags or {})

    def keys():
        return list((keys_and_tags or {}).keys())

    def get_meta(key):
        return meta_store.setdefault(key, {"tags": list((keys_and_tags or {}).get(key, []))})

    def set_meta(key, meta):
        meta_store[key] = meta

    vault.has.side_effect = has
    vault.keys.side_effect = keys
    vault.get_meta.side_effect = get_meta
    vault.set_meta.side_effect = set_meta
    return vault


def test_tag_add_command(runner):
    vault = _mock_vault({"DB_URL": []})
    with patch("envault.cli_tags.Vault.open", return_value=vault):
        result = runner.invoke(tag_cli, ["add", "myvault", "DB_URL", "database", "--password", "secret"])
    assert result.exit_code == 0
    assert "database" in result.output


def test_tag_add_missing_key(runner):
    vault = _mock_vault({})
    with patch("envault.cli_tags.Vault.open", return_value=vault):
        result = runner.invoke(tag_cli, ["add", "myvault", "GHOST", "x", "--password", "pw"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_tag_remove_command(runner):
    vault = _mock_vault({"API_KEY": ["secret"]})
    with patch("envault.cli_tags.Vault.open", return_value=vault):
        result = runner.invoke(tag_cli, ["remove", "myvault", "API_KEY", "secret", "--password", "pw"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_tag_list_all(runner):
    vault = _mock_vault({"DB_URL": ["prod"], "SECRET": ["sensitive"]})
    with patch("envault.cli_tags.Vault.open", return_value=vault):
        result = runner.invoke(tag_cli, ["list", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "prod" in result.output


def test_tag_list_filter_by_tag(runner):
    vault = _mock_vault({"DB_URL": ["prod"], "TOKEN": ["dev"]})
    with patch("envault.cli_tags.Vault.open", return_value=vault):
        result = runner.invoke(tag_cli, ["list", "myvault", "--tag", "prod", "--password", "pw"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "TOKEN" not in result.output


def test_tag_list_no_tags(runner):
    vault = _mock_vault({"A": [], "B": []})
    with patch("envault.cli_tags.Vault.open", return_value=vault):
        result = runner.invoke(tag_cli, ["list", "myvault", "--password", "pw"])
    assert result.exit_code == 0
    assert "No tags defined" in result.output
