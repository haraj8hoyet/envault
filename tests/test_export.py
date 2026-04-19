"""Tests for envault.export module."""

import json
import pytest

from envault.export import export_variables, SUPPORTED_FORMATS


SAMPLE_VARS = {
    "DATABASE_URL": "postgres://localhost/db",
    "API_KEY": "abc123",
    "DEBUG": "true",
}


def test_dotenv_format_contains_all_keys():
    output = export_variables(SAMPLE_VARS, fmt="dotenv")
    for key in SAMPLE_VARS:
        assert key in output


def test_dotenv_format_quoted_values():
    output = export_variables(SAMPLE_VARS, fmt="dotenv")
    assert 'DATABASE_URL="postgres://localhost/db"' in output


def test_dotenv_format_sorted():
    output = export_variables(SAMPLE_VARS, fmt="dotenv")
    keys_in_output = [line.split("=")[0] for line in output.strip().splitlines()]
    assert keys_in_output == sorted(SAMPLE_VARS.keys())


def test_shell_format_uses_export():
    output = export_variables(SAMPLE_VARS, fmt="shell")
    for line in output.strip().splitlines():
        assert line.startswith("export ")


def test_shell_format_contains_all_keys():
    output = export_variables(SAMPLE_VARS, fmt="shell")
    for key in SAMPLE_VARS:
        assert key in output


def test_json_format_is_valid_json():
    output = export_variables(SAMPLE_VARS, fmt="json")
    parsed = json.loads(output)
    assert parsed == SAMPLE_VARS


def test_json_format_sorted_keys():
    output = export_variables(SAMPLE_VARS, fmt="json")
    parsed = json.loads(output)
    assert list(parsed.keys()) == sorted(SAMPLE_VARS.keys())


def test_escaped_quotes_in_values():
    vars_with_quotes = {"MSG": 'say "hello"'}
    for fmt in ("dotenv", "shell"):
        output = export_variables(vars_with_quotes, fmt=fmt)
        assert '\\"' in output


def test_empty_variables():
    for fmt in SUPPORTED_FORMATS:
        output = export_variables({}, fmt=fmt)
        assert isinstance(output, str)


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_variables(SAMPLE_VARS, fmt="xml")
