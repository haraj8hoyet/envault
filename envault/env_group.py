"""Group-based variable management: organize vault keys into named groups."""

from __future__ import annotations

from typing import Dict, List, Optional

META_GROUP_PREFIX = "group:"


class GroupError(Exception):
    pass


def get_group(vault, key: str) -> Optional[str]:
    """Return the group name assigned to a key, or None."""
    meta = vault.get_meta(key)
    return meta.get(META_GROUP_PREFIX + "name") if meta else None


def set_group(vault, key: str, group: str) -> None:
    """Assign a key to a group."""
    if not vault.has(key):
        raise GroupError(f"Key '{key}' not found in vault.")
    if not group.strip():
        raise GroupError("Group name must not be empty.")
    vault.set_meta(key, META_GROUP_PREFIX + "name", group.strip())


def remove_group(vault, key: str) -> None:
    """Remove group assignment from a key."""
    if not vault.has(key):
        raise GroupError(f"Key '{key}' not found in vault.")
    vault.delete_meta(key, META_GROUP_PREFIX + "name")


def list_groups(vault) -> Dict[str, List[str]]:
    """Return a mapping of group name -> list of keys."""
    groups: Dict[str, List[str]] = {}
    for key in vault.keys():
        grp = get_group(vault, key)
        if grp:
            groups.setdefault(grp, []).append(key)
    return groups


def keys_in_group(vault, group: str) -> List[str]:
    """Return all keys belonging to a specific group."""
    return [
        key for key in vault.keys()
        if get_group(vault, key) == group
    ]


def rename_group(vault, old_name: str, new_name: str) -> int:
    """Rename all occurrences of a group. Returns number of keys updated."""
    if not new_name.strip():
        raise GroupError("New group name must not be empty.")
    keys = keys_in_group(vault, old_name)
    for key in keys:
        vault.set_meta(key, META_GROUP_PREFIX + "name", new_name.strip())
    return len(keys)
