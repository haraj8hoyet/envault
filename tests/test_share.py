"""Tests for envault.share — signed bundle creation and verification."""

import json
import time
import pytest
from unittest.mock import patch

from envault.share import (
    create_bundle,
    open_bundle,
    ShareError,
    DEFAULT_TTL_SECONDS,
)

SECRET = "supersecret"
VARS = {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_create_bundle_returns_json_string():
    bundle = create_bundle(VARS, SECRET)
    data = json.loads(bundle)
    assert "payload" in data
    assert "signature" in data


def test_open_bundle_roundtrip():
    bundle = create_bundle(VARS, SECRET)
    result = open_bundle(bundle, SECRET)
    assert result == VARS


def test_open_bundle_wrong_secret_raises():
    bundle = create_bundle(VARS, SECRET)
    with pytest.raises(ShareError, match="invalid"):
        open_bundle(bundle, "wrongsecret")


def test_open_bundle_expired_raises():
    bundle = create_bundle(VARS, SECRET, ttl=10)
    future = time.time() + 20
    with patch("envault.share.time") as mock_time:
        mock_time.time.return_value = future
        with pytest.raises(ShareError, match="expired"):
            open_bundle(bundle, SECRET)


def test_create_bundle_with_label():
    bundle = create_bundle(VARS, SECRET, label="staging")
    data = json.loads(bundle)
    payload = json.loads(data["payload"])
    assert payload["label"] == "staging"


def test_create_bundle_empty_variables_raises():
    with pytest.raises(ShareError, match="no variables"):
        create_bundle({}, SECRET)


def test_open_bundle_malformed_raises():
    with pytest.raises(ShareError, match="Malformed"):
        open_bundle("not-json", SECRET)


def test_open_bundle_tampered_payload_raises():
    bundle = create_bundle(VARS, SECRET)
    data = json.loads(bundle)
    # Tamper with payload
    payload = json.loads(data["payload"])
    payload["variables"]["INJECTED"] = "evil"
    data["payload"] = json.dumps(payload)
    tampered = json.dumps(data)
    with pytest.raises(ShareError, match="invalid"):
        open_bundle(tampered, SECRET)


def test_bundle_contains_version():
    bundle = create_bundle(VARS, SECRET)
    data = json.loads(bundle)
    payload = json.loads(data["payload"])
    assert payload["version"] == 1


def test_bundle_respects_ttl():
    bundle = create_bundle(VARS, SECRET, ttl=60)
    data = json.loads(bundle)
    payload = json.loads(data["payload"])
    assert payload["expires_at"] - payload["created_at"] == pytest.approx(60, abs=1)
