"""Template rendering: substitute vault variables into template strings."""

import re
from typing import Optional


class TemplateError(Exception):
    pass


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_string(template: str, variables: dict, strict: bool = True) -> str:
    """Render a template string, replacing {{VAR}} placeholders with vault values.

    Args:
        template: String containing {{VAR}} placeholders.
        variables: Mapping of variable names to values.
        strict: If True, raise TemplateError for missing variables.
                If False, leave unresolved placeholders as-is.

    Returns:
        Rendered string with placeholders substituted.
    """
    missing = []

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in variables:
            return variables[key]
        if strict:
            missing.append(key)
            return match.group(0)
        return match.group(0)

    result = _PLACEHOLDER_RE.sub(_replace, template)

    if strict and missing:
        raise TemplateError(
            f"Template references undefined variable(s): {', '.join(sorted(missing))}"
        )

    return result


def render_file(
    template_path: str,
    variables: dict,
    output_path: Optional[str] = None,
    strict: bool = True,
) -> str:
    """Read a template file, render it, and optionally write the result.

    Args:
        template_path: Path to the template file.
        variables: Mapping of variable names to values.
        output_path: If provided, write rendered content to this path.
        strict: Passed through to render_string.

    Returns:
        The rendered content as a string.
    """
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()

    rendered = render_string(template, variables, strict=strict)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(rendered)

    return rendered


def list_placeholders(template: str) -> list:
    """Return a sorted list of unique placeholder names found in a template."""
    return sorted(set(_PLACEHOLDER_RE.findall(template)))
