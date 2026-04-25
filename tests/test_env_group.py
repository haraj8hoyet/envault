"""Tests for envault.env_group module."""

import pytest

from envault.env_group import (
    GroupError,
    get_group,
    set_group,
    remove_group,
    list_groups,
    keys_in_group,
    rename_group,
    META_GROUP_PREFIX,
)


class FakeVault:
    def __init__(self, data=None, meta=None):
        self._data = dict(data or {})
        self._meta = dict(meta or {})  # key -> {meta_key: value}

    def has(self, key):
        return key in self._data

    def keys(self):
        return list(self._data.keys())

    def get_meta(self, key):
        return dict(self._meta.get(key, {}))

    def set_meta(self, key, meta_key, value):
        self._meta.setdefault(key, {})[meta_key] = value

    def delete_meta(self, key, meta_key):
        self._meta.get(key, {}).pop(meta_key, None)


def _vault_with_groups():
    v = FakeVault(data={"DB_HOST": "localhost", "DB_PASS": "secret", "APP_KEY": "abc"})
    v.set_meta("DB_HOST", META_GROUP_PREFIX + "name", "database")
    v.set_meta("DB_PASS", META_GROUP_PREFIX + "name", "database")
    v.set_meta("APP_KEY", META_GROUP_PREFIX + "name", "app")
    return v


def test_get_group_returns_assigned_group():
    v = _vault_with_groups()
    assert get_group(v, "DB_HOST") == "database"


def test_get_group_returns_none_when_unassigned():
    v = FakeVault(data={"UNTAGGED": "val"})
    assert get_group(v, "UNTAGGED") is None


def test_set_group_assigns_correctly():
    v = FakeVault(data={"MY_KEY": "value"})
    set_group(v, "MY_KEY", "mygroup")
    assert get_group(v, "MY_KEY") == "mygroup"


def test_set_group_missing_key_raises():
    v = FakeVault()
    with pytest.raises(GroupError, match="not found"):
        set_group(v, "MISSING", "grp")


def test_set_group_empty_name_raises():
    v = FakeVault(data={"K": "v"})
    with pytest.raises(GroupError, match="empty"):
        set_group(v, "K", "   ")


def test_remove_group_clears_assignment():
    v = _vault_with_groups()
    remove_group(v, "DB_HOST")
    assert get_group(v, "DB_HOST") is None


def test_remove_group_missing_key_raises():
    v = FakeVault()
    with pytest.raises(GroupError, match="not found"):
        remove_group(v, "GHOST")


def test_list_groups_returns_all():
    v = _vault_with_groups()
    groups = list_groups(v)
    assert set(groups.keys()) == {"database", "app"}
    assert set(groups["database"]) == {"DB_HOST", "DB_PASS"}
    assert groups["app"] == ["APP_KEY"]


def test_list_groups_empty_when_no_assignments():
    v = FakeVault(data={"A": "1", "B": "2"})
    assert list_groups(v) == {}


def test_keys_in_group_filters_correctly():
    v = _vault_with_groups()
    db_keys = keys_in_group(v, "database")
    assert set(db_keys) == {"DB_HOST", "DB_PASS"}


def test_keys_in_group_empty_for_unknown_group():
    v = _vault_with_groups()
    assert keys_in_group(v, "nonexistent") == []


def test_rename_group_updates_all_keys():
    v = _vault_with_groups()
    count = rename_group(v, "database", "db")
    assert count == 2
    assert get_group(v, "DB_HOST") == "db"
    assert get_group(v, "DB_PASS") == "db"
    assert get_group(v, "APP_KEY") == "app"  # unchanged


def test_rename_group_empty_new_name_raises():
    v = _vault_with_groups()
    with pytest.raises(GroupError, match="empty"):
        rename_group(v, "database", "")


def test_rename_group_returns_zero_for_unknown():
    v = _vault_with_groups()
    count = rename_group(v, "unknown_group", "new_name")
    assert count == 0
