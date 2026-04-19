"""Tests for envault.import_vars module."""

import json
import os
import pytest
from pathlib import Path

from envault.import_vars import (
    parse_dotenv,
    parse_json,
    parse_shell,
    import_from_file,
    import_from_env,
)


def test_parse_dotenv_basic():
    content = "KEY=value\nFOO=bar"
    result = parse_dotenv(content)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_dotenv_ignores_comments():
    content = "# comment\nKEY=value"
    result = parse_dotenv(content)
    assert "KEY" in result
    assert len(result) == 1


def test_parse_dotenv_strips_quotes():
    content = 'KEY="hello world"\nFOO=\'bar\''
    result = parse_dotenv(content)
    assert result["KEY"] == "hello world"
    assert result["FOO"] == "bar"


def test_parse_dotenv_ignores_blank_lines():
    content = "\nKEY=value\n\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_json_basic():
    content = json.dumps({"KEY": "value", "NUM": 42})
    result = parse_json(content)
    assert result == {"KEY": "value", "NUM": "42"}


def test_parse_json_non_dict_raises():
    with pytest.raises(ValueError):
        parse_json(json.dumps(["a", "b"]))


def test_parse_shell_basic():
    content = "export KEY=value\nexport FOO=bar"
    result = parse_shell(content)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_shell_strips_quotes():
    content = 'export KEY="hello"'
    result = parse_shell(content)
    assert result["KEY"] == "hello"


def test_import_from_file_dotenv(tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1\nB=2")
    result = import_from_file(str(f))
    assert result == {"A": "1", "B": "2"}


def test_import_from_file_json(tmp_path):
    f = tmp_path / "vars.json"
    f.write_text(json.dumps({"X": "y"}))
    result = import_from_file(str(f))
    assert result == {"X": "y"}


def test_import_from_file_explicit_format(tmp_path):
    f = tmp_path / "myfile.txt"
    f.write_text("export Z=99")
    result = import_from_file(str(f), fmt="shell")
    assert result["Z"] == "99"


def test_import_from_env_all():
    os.environ["_ENVAULT_TEST"] = "hello"
    result = import_from_env()
    assert "_ENVAULT_TEST" in result
    del os.environ["_ENVAULT_TEST"]


def test_import_from_env_filtered():
    os.environ["_ENVAULT_A"] = "1"
    os.environ["_ENVAULT_B"] = "2"
    result = import_from_env(keys=["_ENVAULT_A", "_ENVAULT_MISSING"])
    assert result == {"_ENVAULT_A": "1"}
    del os.environ["_ENVAULT_A"]
    del os.environ["_ENVAULT_B"]
