"""Tests for envault/tags.py."""

from __future__ import annotations

import pytest

from envault.tags import add_tag, remove_tag, list_by_tag, all_tags, TagError


class FakeVault:
    """Minimal vault stub for tag tests."""

    def __init__(self, keys_data=None):
        self._data = keys_data or {}
        self._meta = {k: {} for k in self._data}

    def has(self, key: str) -> bool:
        return key in self._data

    def keys(self):
        return list(self._data.keys())

    def get_meta(self, key: str) -> dict:
        return self._meta.setdefault(key, {})

    def set_meta(self, key: str, meta: dict):
        self._meta[key] = meta


def _vault(*keys):
    return FakeVault({k: "val" for k in keys})


def test_add_tag_basic():
    v = _vault("DB_URL")
    result = add_tag(v, "DB_URL", "database")
    assert "database" in result


def test_add_tag_normalises_case():
    v = _vault("DB_URL")
    add_tag(v, "DB_URL", "Database")
    assert "database" in v.get_meta("DB_URL")["tags"]


def test_add_tag_deduplicates():
    v = _vault("DB_URL")
    add_tag(v, "DB_URL", "db")
    add_tag(v, "DB_URL", "db")
    assert v.get_meta("DB_URL")["tags"].count("db") == 1


def test_add_tag_missing_key_raises():
    v = _vault()
    with pytest.raises(TagError, match="not found"):
        add_tag(v, "MISSING", "x")


def test_add_empty_tag_raises():
    v = _vault("K")
    with pytest.raises(TagError, match="empty"):
        add_tag(v, "K", "   ")


def test_remove_tag():
    v = _vault("API_KEY")
    add_tag(v, "API_KEY", "secret")
    remaining = remove_tag(v, "API_KEY", "secret")
    assert "secret" not in remaining


def test_remove_nonexistent_tag_is_idempotent():
    v = _vault("API_KEY")
    result = remove_tag(v, "API_KEY", "ghost")
    assert result == []


def test_remove_tag_missing_key_raises():
    v = _vault()
    with pytest.raises(TagError):
        remove_tag(v, "NOPE", "t")


def test_list_by_tag():
    v = _vault("A", "B", "C")
    add_tag(v, "A", "prod")
    add_tag(v, "C", "prod")
    result = list_by_tag(v, "prod")
    assert result == ["A", "C"]


def test_list_by_tag_no_match():
    v = _vault("A")
    assert list_by_tag(v, "unknown") == []


def test_all_tags_returns_only_tagged_keys():
    v = _vault("X", "Y", "Z")
    add_tag(v, "X", "alpha")
    add_tag(v, "Z", "beta")
    mapping = all_tags(v)
    assert "X" in mapping
    assert "Z" in mapping
    assert "Y" not in mapping


def test_all_tags_empty_vault():
    v = _vault("A", "B")
    assert all_tags(v) == {}
