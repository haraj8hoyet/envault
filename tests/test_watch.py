"""Tests for envault.watch."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from envault.watch import watch_vault, diff_checksum, WatchError
from envault.cli_watch import watch_cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self, data):
        self._data = data

    def keys(self):
        return list(self._data.keys())

    def get(self, k):
        return self._data[k]


def _mock_open(data):
    vault = _FakeVault(data)
    return MagicMock(return_value=vault)


# ---------------------------------------------------------------------------
# Unit tests for watch_vault
# ---------------------------------------------------------------------------

def test_watch_raises_for_missing_vault():
    with patch("envault.watch.vault_exists", return_value=False):
        with pytest.raises(WatchError, match="does not exist"):
            watch_vault("ghost", "pw", on_change=lambda n, c: None, max_iterations=1)


def test_watch_calls_on_change_when_vault_changes():
    calls = []

    seq = [{"A": "1"}, {"A": "2"}]  # second call returns different data
    call_count = [0]

    def fake_open(name, pw):
        idx = min(call_count[0], len(seq) - 1)
        call_count[0] += 1
        return _FakeVault(seq[idx])

    with patch("envault.watch.vault_exists", return_value=True), \
         patch("envault.watch.Vault") as MockVault, \
         patch("envault.watch.time.sleep"):
        MockVault.open.side_effect = fake_open
        watch_vault("myvault", "pw", on_change=lambda n, c: calls.append(c), max_iterations=1)

    assert len(calls) == 1


def test_watch_does_not_call_on_change_when_unchanged():
    calls = []

    fixed_data = {"KEY": "value"}

    with patch("envault.watch.vault_exists", return_value=True), \
         patch("envault.watch.Vault") as MockVault, \
         patch("envault.watch.time.sleep"):
        MockVault.open.return_value = _FakeVault(fixed_data)
        watch_vault("myvault", "pw", on_change=lambda n, c: calls.append(c), max_iterations=3)

    assert calls == []


def test_diff_checksum_detects_change():
    assert diff_checksum("abc", "def") is True


def test_diff_checksum_same_returns_false():
    assert diff_checksum("abc", "abc") is False


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_watch_vault_not_found(runner):
    with patch("envault.cli_watch.vault_exists", return_value=False):
        result = runner.invoke(watch_cli, ["start", "ghost", "--password", "pw"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_cli_watch_prints_change(runner):
    fixed_then_changed = [{"K": "1"}, {"K": "2"}]
    call_count = [0]

    def fake_open(name, pw):
        idx = min(call_count[0], 1)
        call_count[0] += 1
        v = MagicMock()
        v.keys.return_value = ["K"]
        v.get.return_value = fixed_then_changed[idx]["K"]
        return v

    with patch("envault.cli_watch.vault_exists", return_value=True), \
         patch("envault.watch.vault_exists", return_value=True), \
         patch("envault.watch.Vault") as MockVault, \
         patch("envault.watch.time.sleep"):
        MockVault.open.side_effect = fake_open
        result = runner.invoke(
            watch_cli,
            ["start", "myvault", "--password", "pw", "--interval", "0"],
            catch_exceptions=False,
        )

    assert "Watching" in result.output
