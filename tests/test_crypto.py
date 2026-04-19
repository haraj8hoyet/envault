"""Tests for envault.crypto encryption/decryption."""

import pytest
from envault.crypto import encrypt, decrypt


def test_encrypt_returns_string():
    token = encrypt("hello", "password123")
    assert isinstance(token, str)
    assert len(token) > 0


def test_decrypt_roundtrip():
    plaintext = "SECRET_KEY=abc123"
    password = "strongpassword"
    token = encrypt(plaintext, password)
    result = decrypt(token, password)
    assert result == plaintext


def test_different_passwords_produce_different_tokens():
    plaintext = "VALUE=42"
    token1 = encrypt(plaintext, "pass1")
    token2 = encrypt(plaintext, "pass2")
    assert token1 != token2


def test_wrong_password_raises():
    token = encrypt("secret", "correct")
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong")


def test_corrupted_token_raises():
    with pytest.raises(ValueError):
        decrypt("notavalidtoken!!!!", "password")


def test_encrypt_same_plaintext_differs_each_call():
    """Each encryption should produce a unique token due to random salt/nonce."""
    t1 = encrypt("same", "pass")
    t2 = encrypt("same", "pass")
    assert t1 != t2
