"""Search and filter environment variables across vaults."""
from fnmatch import fnmatch
from typing import Optional
from envault.vault import Vault


def search_keys(vault: Vault, pattern: str) -> dict:
    """Return key-value pairs where key matches the glob pattern."""
    all_vars = vault.all()
    return {k: v for k, v in all_vars.items() if fnmatch(k.upper(), pattern.upper())}


def search_values(vault: Vault, substring: str, case_sensitive: bool = False) -> dict:
    """Return key-value pairs where value contains the substring."""
    all_vars = vault.all()
    if not case_sensitive:
        substring = substring.lower()
    result = {}
    for k, v in all_vars.items():
        haystack = v if case_sensitive else v.lower()
        if substring in haystack:
            result[k] = v
    return result


def search_by_prefix(vault: Vault, prefix: str) -> dict:
    """Return key-value pairs where key starts with the given prefix."""
    prefix_upper = prefix.upper()
    return {k: v for k, v in vault.all().items() if k.upper().startswith(prefix_upper)}


def filter_keys(vault: Vault, keys: list) -> dict:
    """Return only the specified keys that exist in the vault."""
    all_vars = vault.all()
    return {k: all_vars[k] for k in keys if k in all_vars}
