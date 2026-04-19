"""Tests for envault.audit module."""

import pytest
from pathlib import Path

from envault.audit import record_event, read_events, clear_audit_log


@pytest.fixture
def audit_dir(tmp_path):
    return str(tmp_path)


def test_record_and_read_event(audit_dir):
    record_event("myvault", "create", base_dir=audit_dir)
    events = read_events("myvault", base_dir=audit_dir)
    assert len(events) == 1
    assert events[0]["action"] == "create"
    assert "timestamp" in events[0]
    assert "key" not in events[0]


def test_record_event_with_key(audit_dir):
    record_event("myvault", "set", key="API_KEY", base_dir=audit_dir)
    events = read_events("myvault", base_dir=audit_dir)
    assert events[0]["key"] == "API_KEY"
    assert events[0]["action"] == "set"


def test_multiple_events_appended(audit_dir):
    record_event("myvault", "set", key="FOO", base_dir=audit_dir)
    record_event("myvault", "set", key="BAR", base_dir=audit_dir)
    record_event("myvault", "delete", key="FOO", base_dir=audit_dir)
    events = read_events("myvault", base_dir=audit_dir)
    assert len(events) == 3
    assert events[2]["action"] == "delete"


def test_read_events_empty_when_no_log(audit_dir):
    events = read_events("nonexistent", base_dir=audit_dir)
    assert events == []


def test_clear_audit_log(audit_dir):
    record_event("myvault", "create", base_dir=audit_dir)
    clear_audit_log("myvault", base_dir=audit_dir)
    events = read_events("myvault", base_dir=audit_dir)
    assert events == []


def test_clear_nonexistent_log_does_not_raise(audit_dir):
    clear_audit_log("ghost", base_dir=audit_dir)  # should not raise


def test_events_are_ordered_chronologically(audit_dir):
    for action in ["create", "set", "get"]:
        record_event("myvault", action, base_dir=audit_dir)
    events = read_events("myvault", base_dir=audit_dir)
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)
