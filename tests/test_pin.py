"""Tests for envault.pin module."""

import pytest
from pathlib import Path
from envault.pin import set_pin, verify_pin, clear_pin, has_pin, PinError


@pytest.fixture
def pin_dir(tmp_path):
    return str(tmp_path)


def test_set_and_verify_pin(pin_dir):
    set_pin("myvault", "s3cret", "1234", base_dir=pin_dir)
    assert verify_pin("myvault", "s3cret", "1234", base_dir=pin_dir) is True


def test_wrong_pin_returns_false(pin_dir):
    set_pin("myvault", "s3cret", "1234", base_dir=pin_dir)
    assert verify_pin("myvault", "s3cret", "9999", base_dir=pin_dir) is False


def test_wrong_password_returns_false(pin_dir):
    set_pin("myvault", "s3cret", "1234", base_dir=pin_dir)
    assert verify_pin("myvault", "wrongpass", "1234", base_dir=pin_dir) is False


def test_verify_no_pin_raises(pin_dir):
    with pytest.raises(PinError, match="No PIN set"):
        verify_pin("ghost", "pass", "0000", base_dir=pin_dir)


def test_pin_too_short_raises(pin_dir):
    with pytest.raises(PinError, match="at least 4"):
        set_pin("myvault", "s3cret", "12", base_dir=pin_dir)


def test_empty_pin_raises(pin_dir):
    with pytest.raises(PinError, match="must not be empty"):
        set_pin("myvault", "s3cret", "", base_dir=pin_dir)


def test_has_pin_false_before_set(pin_dir):
    assert has_pin("myvault", base_dir=pin_dir) is False


def test_has_pin_true_after_set(pin_dir):
    set_pin("myvault", "s3cret", "1234", base_dir=pin_dir)
    assert has_pin("myvault", base_dir=pin_dir) is True


def test_clear_pin_removes_file(pin_dir):
    set_pin("myvault", "s3cret", "1234", base_dir=pin_dir)
    clear_pin("myvault", base_dir=pin_dir)
    assert has_pin("myvault", base_dir=pin_dir) is False


def test_clear_pin_idempotent(pin_dir):
    # Clearing a non-existent PIN should not raise
    clear_pin("ghost", base_dir=pin_dir)


def test_overwrite_pin(pin_dir):
    set_pin("myvault", "s3cret", "1234", base_dir=pin_dir)
    set_pin("myvault", "s3cret", "5678", base_dir=pin_dir)
    assert verify_pin("myvault", "s3cret", "5678", base_dir=pin_dir) is True
    assert verify_pin("myvault", "s3cret", "1234", base_dir=pin_dir) is False


def test_different_vaults_independent(pin_dir):
    set_pin("vault_a", "pass_a", "1111", base_dir=pin_dir)
    set_pin("vault_b", "pass_b", "2222", base_dir=pin_dir)
    assert verify_pin("vault_a", "pass_a", "1111", base_dir=pin_dir) is True
    assert verify_pin("vault_b", "pass_b", "2222", base_dir=pin_dir) is True
    assert verify_pin("vault_a", "pass_a", "2222", base_dir=pin_dir) is False
