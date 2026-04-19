"""Tests for envault/search.py."""
import pytest
from unittest.mock import MagicMock
from envault import search as search_mod


def _make_vault(data: dict):
    vault = MagicMock()
    vault.all.return_value = data
    return vault


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "topsecret",
    "APP_DEBUG": "true",
    "REDIS_URL": "redis://localhost",
}


def test_search_keys_glob():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_keys(vault, "DB_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_keys_exact():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_keys(vault, "APP_SECRET")
    assert result == {"APP_SECRET": "topsecret"}


def test_search_keys_no_match():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_keys(vault, "MISSING_*")
    assert result == {}


def test_search_keys_case_insensitive():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_keys(vault, "db_*")
    assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_values_substring():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_values(vault, "localhost")
    assert "DB_HOST" in result
    assert "REDIS_URL" in result


def test_search_values_case_insensitive():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_values(vault, "LOCALHOST")
    assert "DB_HOST" in result


def test_search_values_case_sensitive_no_match():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_values(vault, "LOCALHOST", case_sensitive=True)
    assert result == {}


def test_search_by_prefix():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_by_prefix(vault, "APP_")
    assert set(result.keys()) == {"APP_SECRET", "APP_DEBUG"}


def test_search_by_prefix_case_insensitive():
    vault = _make_vault(SAMPLE)
    result = search_mod.search_by_prefix(vault, "app_")
    assert set(result.keys()) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_keys_existing():
    vault = _make_vault(SAMPLE)
    result = search_mod.filter_keys(vault, ["DB_HOST", "APP_SECRET"])
    assert result == {"DB_HOST": "localhost", "APP_SECRET": "topsecret"}


def test_filter_keys_partial_missing():
    vault = _make_vault(SAMPLE)
    result = search_mod.filter_keys(vault, ["DB_HOST", "NONEXISTENT"])
    assert result == {"DB_HOST": "localhost"}
