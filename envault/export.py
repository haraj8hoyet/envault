"""Export vault variables to shell-compatible formats."""

from typing import Dict, Optional

SUPPORTED_FORMATS = ("dotenv", "shell", "json")


def export_dotenv(variables: Dict[str, str]) -> str:
    """Export variables in .env file format."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_shell(variables: Dict[str, str]) -> str:
    """Export variables as shell export statements."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(variables: Dict[str, str]) -> str:
    """Export variables as a JSON object."""
    import json
    return json.dumps(variables, indent=2, sort_keys=True) + "\n"


def export_variables(variables: Dict[str, str], fmt: str = "dotenv") -> str:
    """Export variables in the specified format.

    Args:
        variables: Dictionary of environment variable key-value pairs.
        fmt: Output format — one of 'dotenv', 'shell', or 'json'.

    Returns:
        Formatted string representation of the variables.

    Raises:
        ValueError: If an unsupported format is specified.
    """
    if fmt == "dotenv":
        return export_dotenv(variables)
    elif fmt == "shell":
        return export_shell(variables)
    elif fmt == "json":
        return export_json(variables)
    else:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
