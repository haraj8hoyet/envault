"""Import environment variables into a vault from various sources."""

import json
import os
from pathlib import Path
from typing import Dict, Optional


def parse_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env file content into a dictionary."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def parse_json(content: str) -> Dict[str, str]:
    """Parse a JSON object into a dictionary of strings."""
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return {str(k): str(v) for k, v in data.items()}


def parse_shell(content: str) -> Dict[str, str]:
    """Parse shell export statements into a dictionary."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def import_from_file(filepath: str, fmt: Optional[str] = None) -> Dict[str, str]:
    """Read a file and parse it based on format or file extension."""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")

    if fmt is None:
        suffix = path.suffix.lower()
        if suffix == ".json":
            fmt = "json"
        elif suffix == ".sh":
            fmt = "shell"
        else:
            fmt = "dotenv"

    if fmt == "json":
        return parse_json(content)
    elif fmt == "shell":
        return parse_shell(content)
    else:
        return parse_dotenv(content)


def import_from_env(keys: Optional[list] = None) -> Dict[str, str]:
    """Import variables from the current process environment."""
    if keys:
        return {k: os.environ[k] for k in keys if k in os.environ}
    return dict(os.environ)
