"""Tests for envault.template module."""

import os
import pytest

from envault.template import (
    TemplateError,
    list_placeholders,
    render_file,
    render_string,
)


# ---------------------------------------------------------------------------
# render_string
# ---------------------------------------------------------------------------


def test_render_string_basic():
    result = render_string("Hello, {{NAME}}!", {"NAME": "Alice"})
    assert result == "Hello, Alice!"


def test_render_string_multiple_placeholders():
    tpl = "{{PROTO}}://{{HOST}}:{{PORT}}"
    result = render_string(tpl, {"PROTO": "https", "HOST": "example.com", "PORT": "443"})
    assert result == "https://example.com:443"


def test_render_string_repeated_placeholder():
    result = render_string("{{X}} and {{X}}", {"X": "42"})
    assert result == "42 and 42"


def test_render_string_no_placeholders():
    result = render_string("no placeholders here", {})
    assert result == "no placeholders here"


def test_render_string_strict_raises_on_missing():
    with pytest.raises(TemplateError, match="MISSING"):
        render_string("{{PRESENT}} {{MISSING}}", {"PRESENT": "ok"}, strict=True)


def test_render_string_non_strict_leaves_unresolved():
    result = render_string("{{PRESENT}} {{MISSING}}", {"PRESENT": "ok"}, strict=False)
    assert result == "ok {{MISSING}}"


def test_render_string_whitespace_inside_braces():
    result = render_string("{{ NAME }}", {"NAME": "World"})
    assert result == "World"


def test_render_string_empty_variables_strict_raises():
    with pytest.raises(TemplateError):
        render_string("{{FOO}}", {}, strict=True)


# ---------------------------------------------------------------------------
# list_placeholders
# ---------------------------------------------------------------------------


def test_list_placeholders_basic():
    placeholders = list_placeholders("{{FOO}} and {{BAR}}")
    assert placeholders == ["BAR", "FOO"]


def test_list_placeholders_deduplicates():
    placeholders = list_placeholders("{{X}} {{X}} {{Y}}")
    assert placeholders == ["X", "Y"]


def test_list_placeholders_empty():
    assert list_placeholders("nothing here") == []


# ---------------------------------------------------------------------------
# render_file
# ---------------------------------------------------------------------------


def test_render_file_reads_and_renders(tmp_path):
    tpl_file = tmp_path / "config.tpl"
    tpl_file.write_text("DB_HOST={{DB_HOST}}\nDB_PORT={{DB_PORT}}\n")

    result = render_file(str(tpl_file), {"DB_HOST": "localhost", "DB_PORT": "5432"})
    assert result == "DB_HOST=localhost\nDB_PORT=5432\n"


def test_render_file_writes_output(tmp_path):
    tpl_file = tmp_path / "nginx.conf.tpl"
    out_file = tmp_path / "nginx.conf"
    tpl_file.write_text("server_name {{DOMAIN}};\n")

    render_file(str(tpl_file), {"DOMAIN": "example.com"}, output_path=str(out_file))

    assert out_file.read_text() == "server_name example.com;\n"


def test_render_file_strict_raises_on_missing(tmp_path):
    tpl_file = tmp_path / "bad.tpl"
    tpl_file.write_text("{{UNDEFINED}}")

    with pytest.raises(TemplateError):
        render_file(str(tpl_file), {}, strict=True)
