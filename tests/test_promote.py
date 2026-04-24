"""Tests for envault.env_promote and envault.cli_promote."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envault.env_promote import promote_variables, PromoteError, PromoteResult
from envault.cli_promote import promote_cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_vault(data: dict[str, str], name: str = "src") -> MagicMock:
    vault = MagicMock()
    vault.name = name
    vault.keys.return_value = list(data.keys())
    vault.has.side_effect = lambda k: k in data
    vault.get.side_effect = lambda k: data[k]
    vault.set.side_effect = lambda k, v: data.update({k: v})
    vault.save.return_value = None
    return vault


# ---------------------------------------------------------------------------
# Unit tests for promote_variables
# ---------------------------------------------------------------------------

def test_promote_all_keys_to_empty_destination():
    src = _make_vault({"A": "1", "B": "2"}, name="src")
    dst_data: dict[str, str] = {}
    dst = _make_vault(dst_data, name="dst")

    result = promote_variables(src, dst, overwrite=False)

    assert set(result.promoted) == {"A", "B"}
    assert result.skipped == []
    assert result.overwritten == []
    assert dst_data == {"A": "1", "B": "2"}


def test_promote_skips_existing_keys_when_no_overwrite():
    src = _make_vault({"A": "new", "B": "2"}, name="src")
    dst_data = {"A": "old"}
    dst = _make_vault(dst_data, name="dst")

    result = promote_variables(src, dst, overwrite=False)

    assert "A" in result.skipped
    assert "B" in result.promoted
    assert dst_data["A"] == "old"  # not overwritten


def test_promote_overwrites_existing_keys_when_flag_set():
    src = _make_vault({"A": "new"}, name="src")
    dst_data = {"A": "old"}
    dst = _make_vault(dst_data, name="dst")

    result = promote_variables(src, dst, overwrite=True)

    assert "A" in result.overwritten
    assert dst_data["A"] == "new"


def test_promote_specific_keys_only():
    src = _make_vault({"A": "1", "B": "2", "C": "3"}, name="src")
    dst_data: dict[str, str] = {}
    dst = _make_vault(dst_data, name="dst")

    result = promote_variables(src, dst, keys=["A", "C"])

    assert set(result.promoted) == {"A", "C"}
    assert "B" not in dst_data


def test_promote_raises_when_key_missing_in_source():
    src = _make_vault({"A": "1"}, name="src")
    dst = _make_vault({}, name="dst")

    with pytest.raises(PromoteError, match="MISSING"):
        promote_variables(src, dst, keys=["MISSING"])


def test_promote_result_summary_nothing():
    result = PromoteResult()
    assert result.summary() == "Nothing to promote."


def test_promote_result_summary_mixed():
    result = PromoteResult()
    result.promoted = ["B"]
    result.overwritten = ["A"]
    result.skipped = ["C"]
    summary = result.summary()
    assert "Promoted" in summary
    assert "Overwritten" in summary
    assert "Skipped" in summary


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_promote_run_success(runner):
    src_data = {"KEY": "value"}
    dst_data: dict[str, str] = {}
    src_vault = _make_vault(src_data, name="staging")
    dst_vault = _make_vault(dst_data, name="prod")

    with patch("envault.cli_promote.vault_exists", return_value=True), \
         patch("envault.cli_promote.Vault.open", side_effect=[src_vault, dst_vault]):
        result = runner.invoke(
            promote_cli,
            ["run", "staging", "prod", "--password", "secret"],
        )

    assert result.exit_code == 0
    assert "KEY" in result.output or "Promoted" in result.output


def test_cli_promote_run_source_not_found(runner):
    with patch("envault.cli_promote.vault_exists", side_effect=lambda n: n != "staging"):
        result = runner.invoke(
            promote_cli,
            ["run", "staging", "prod", "--password", "secret"],
        )

    assert result.exit_code != 0
    assert "source vault" in result.output or "source vault" in (result.output + str(result.exception))


def test_cli_promote_run_dest_not_found(runner):
    with patch("envault.cli_promote.vault_exists", side_effect=lambda n: n == "staging"):
        result = runner.invoke(
            promote_cli,
            ["run", "staging", "prod", "--password", "secret"],
        )

    assert result.exit_code != 0
