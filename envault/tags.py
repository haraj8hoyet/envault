"""Tag management for vault variables — assign, remove, and filter by tags."""

from __future__ import annotations

from typing import Dict, List, Set


class TagError(Exception):
    pass


def get_tags(vault, key: str) -> List[str]:
    """Return sorted list of tags for a given key."""
    meta = vault.get_meta(key)
    return sorted(meta.get("tags", []))


def add_tag(vault, key: str, tag: str) -> List[str]:
    """Add a tag to a key. Returns updated tag list."""
    if not vault.has(key):
        raise TagError(f"Key '{key}' not found in vault.")
    tag = tag.strip().lower()
    if not tag:
        raise TagError("Tag must not be empty.")
    meta = vault.get_meta(key)
    tags: Set[str] = set(meta.get("tags", []))
    tags.add(tag)
    meta["tags"] = sorted(tags)
    vault.set_meta(key, meta)
    return meta["tags"]


def remove_tag(vault, key: str, tag: str) -> List[str]:
    """Remove a tag from a key. Returns updated tag list."""
    if not vault.has(key):
        raise TagError(f"Key '{key}' not found in vault.")
    tag = tag.strip().lower()
    meta = vault.get_meta(key)
    tags: Set[str] = set(meta.get("tags", []))
    tags.discard(tag)
    meta["tags"] = sorted(tags)
    vault.set_meta(key, meta)
    return meta["tags"]


def list_by_tag(vault, tag: str) -> List[str]:
    """Return all keys that have the given tag."""
    tag = tag.strip().lower()
    result = []
    for key in vault.keys():
        meta = vault.get_meta(key)
        if tag in meta.get("tags", []):
            result.append(key)
    return sorted(result)


def all_tags(vault) -> Dict[str, List[str]]:
    """Return mapping of key -> tags for all keys that have at least one tag."""
    result = {}
    for key in vault.keys():
        tags = get_tags(vault, key)
        if tags:
            result[key] = tags
    return result
