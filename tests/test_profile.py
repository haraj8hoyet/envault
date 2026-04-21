"""Tests for envault/profile.py"""

import pytest
from envault.profile import (
    ProfileError,
    create_profile,
    delete_profile,
    get_profile,
    list_profiles,
    update_profile,
)


@pytest.fixture
def profile_dir(tmp_path):
    return str(tmp_path)


def test_create_and_list(profile_dir):
    create_profile("dev", ["app", "db"], base_dir=profile_dir)
    assert "dev" in list_profiles(base_dir=profile_dir)


def test_create_duplicate_raises(profile_dir):
    create_profile("dev", ["app"], base_dir=profile_dir)
    with pytest.raises(ProfileError, match="already exists"):
        create_profile("dev", ["db"], base_dir=profile_dir)


def test_get_profile_returns_vaults(profile_dir):
    create_profile("staging", ["api", "cache"], base_dir=profile_dir)
    data = get_profile("staging", base_dir=profile_dir)
    assert data["vaults"] == ["api", "cache"]


def test_get_profile_not_found_raises(profile_dir):
    with pytest.raises(ProfileError, match="not found"):
        get_profile("ghost", base_dir=profile_dir)


def test_delete_profile(profile_dir):
    create_profile("prod", ["app"], base_dir=profile_dir)
    delete_profile("prod", base_dir=profile_dir)
    assert "prod" not in list_profiles(base_dir=profile_dir)


def test_delete_nonexistent_raises(profile_dir):
    with pytest.raises(ProfileError, match="not found"):
        delete_profile("nope", base_dir=profile_dir)


def test_list_profiles_empty(profile_dir):
    assert list_profiles(base_dir=profile_dir) == []


def test_list_profiles_sorted(profile_dir):
    create_profile("prod", ["x"], base_dir=profile_dir)
    create_profile("dev", ["y"], base_dir=profile_dir)
    create_profile("staging", ["z"], base_dir=profile_dir)
    assert list_profiles(base_dir=profile_dir) == ["dev", "prod", "staging"]


def test_update_profile(profile_dir):
    create_profile("dev", ["old"], base_dir=profile_dir)
    update_profile("dev", ["new1", "new2"], base_dir=profile_dir)
    data = get_profile("dev", base_dir=profile_dir)
    assert data["vaults"] == ["new1", "new2"]


def test_update_nonexistent_raises(profile_dir):
    with pytest.raises(ProfileError, match="not found"):
        update_profile("ghost", ["x"], base_dir=profile_dir)


def test_multiple_profiles_independent(profile_dir):
    create_profile("dev", ["a"], base_dir=profile_dir)
    create_profile("prod", ["b", "c"], base_dir=profile_dir)
    assert get_profile("dev", base_dir=profile_dir)["vaults"] == ["a"]
    assert get_profile("prod", base_dir=profile_dir)["vaults"] == ["b", "c"]
