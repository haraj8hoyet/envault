"""Alias support: map short names to vault variable keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.storage import _vault_path


class AliasError(Exception):
    """Raised when an alias operation fails."""


def _alias_file(vault_name: str) -> Path:
    return _vault_path(vault_name).parent / f"{vault_name}.aliases.json"


def _load_aliases(vault_name: str) -> Dict[str, str]:
    path = _alias_file(vault_name)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(vault_name: str, aliases: Dict[str, str]) -> None:
    _alias_file(vault_name).write_text(json.dumps(aliases, indent=2))


def set_alias(vault_name: str, alias: str, key: str) -> None:
    """Create or update an alias pointing to *key*."""
    if not alias:
        raise AliasError("Alias name must not be empty.")
    if not key:
        raise AliasError("Target key must not be empty.")
    aliases = _load_aliases(vault_name)
    aliases[alias] = key
    _save_aliases(vault_name, aliases)


def remove_alias(vault_name: str, alias: str) -> None:
    """Remove an existing alias."""
    aliases = _load_aliases(vault_name)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' does not exist.")
    del aliases[alias]
    _save_aliases(vault_name, aliases)


def resolve_alias(vault_name: str, alias: str) -> Optional[str]:
    """Return the key that *alias* maps to, or None if not found."""
    return _load_aliases(vault_name).get(alias)


def list_aliases(vault_name: str) -> List[Dict[str, str]]:
    """Return all aliases as a list of {alias, key} dicts, sorted by alias."""
    aliases = _load_aliases(vault_name)
    return [{"alias": a, "key": k} for a, k in sorted(aliases.items())]


def clear_aliases(vault_name: str) -> int:
    """Remove all aliases. Returns the number of aliases removed."""
    aliases = _load_aliases(vault_name)
    count = len(aliases)
    _save_aliases(vault_name, {})
    return count
