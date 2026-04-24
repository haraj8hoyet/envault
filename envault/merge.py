"""Merge variables from one vault into another."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple

from envault.vault import Vault


class MergeStrategy(str, Enum):
    SKIP = "skip"        # keep destination value if key exists
    OVERWRITE = "overwrite"  # always overwrite with source value
    PROMPT = "prompt"    # not handled here; caller must resolve


class MergeError(Exception):
    pass


class MergeResult:
    def __init__(self) -> None:
        self.added: List[str] = []
        self.skipped: List[str] = []
        self.overwritten: List[str] = []

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"added={len(self.added)}")
        if self.overwritten:
            parts.append(f"overwritten={len(self.overwritten)}")
        if self.skipped:
            parts.append(f"skipped={len(self.skipped)}")
        return ", ".join(parts) if parts else "no changes"


def merge_vaults(
    src: Vault,
    dst: Vault,
    strategy: MergeStrategy = MergeStrategy.SKIP,
    keys: List[str] | None = None,
) -> MergeResult:
    """Merge variables from *src* into *dst* using the given strategy.

    Args:
        src: Source vault (already opened).
        dst: Destination vault (already opened).
        strategy: Conflict resolution strategy.
        keys: If provided, only merge these specific keys.

    Returns:
        A MergeResult describing what changed.
    """
    result = MergeResult()
    source_keys = keys if keys is not None else src.keys()

    for key in source_keys:
        if not src.has(key):
            raise MergeError(f"Key '{key}' not found in source vault '{src.name}'")

        value = src.get(key)
        if dst.has(key):
            if strategy == MergeStrategy.SKIP:
                result.skipped.append(key)
                continue
            elif strategy == MergeStrategy.OVERWRITE:
                dst.set(key, value)
                result.overwritten.append(key)
            else:
                raise MergeError(
                    f"Strategy '{strategy}' requires caller-side resolution for key '{key}'"
                )
        else:
            dst.set(key, value)
            result.added.append(key)

    return result


def merge_dicts(
    src: Dict[str, str],
    dst: Dict[str, str],
    strategy: MergeStrategy = MergeStrategy.SKIP,
) -> Tuple[Dict[str, str], MergeResult]:
    """Merge two plain dicts and return the merged dict plus a result summary."""
    merged = dict(dst)
    result = MergeResult()

    for key, value in src.items():
        if key in merged:
            if strategy == MergeStrategy.OVERWRITE:
                merged[key] = value
                result.overwritten.append(key)
            else:
                result.skipped.append(key)
        else:
            merged[key] = value
            result.added.append(key)

    return merged, result
