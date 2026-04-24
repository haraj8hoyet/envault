"""Promote variables from one vault to another (e.g. staging -> production)."""

from __future__ import annotations

from typing import Optional

from envault.vault import Vault
from envault.storage import vault_exists


class PromoteError(Exception):
    """Raised when a promotion operation fails."""


class PromoteResult:
    """Summary of a promotion operation."""

    def __init__(self) -> None:
        self.promoted: list[str] = []
        self.skipped: list[str] = []
        self.overwritten: list[str] = []

    def summary(self) -> str:
        lines = []
        if self.promoted:
            lines.append(f"Promoted: {', '.join(sorted(self.promoted))}")
        if self.overwritten:
            lines.append(f"Overwritten: {', '.join(sorted(self.overwritten))}")
        if self.skipped:
            lines.append(f"Skipped: {', '.join(sorted(self.skipped))}")
        return "\n".join(lines) if lines else "Nothing to promote."


def promote_variables(
    src_vault: Vault,
    dst_vault: Vault,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Copy variables from *src_vault* to *dst_vault*.

    Args:
        src_vault: The source vault (already opened).
        dst_vault: The destination vault (already opened).
        keys: Specific keys to promote.  ``None`` means all keys.
        overwrite: If *True*, existing keys in the destination are replaced.

    Returns:
        A :class:`PromoteResult` describing what happened.

    Raises:
        PromoteError: If a requested key is missing from the source vault.
    """
    result = PromoteResult()
    target_keys = keys if keys is not None else list(src_vault.keys())

    for key in target_keys:
        if not src_vault.has(key):
            raise PromoteError(f"Key '{key}' not found in source vault '{src_vault.name}'.")

        value = src_vault.get(key)
        exists_in_dst = dst_vault.has(key)

        if exists_in_dst and not overwrite:
            result.skipped.append(key)
            continue

        dst_vault.set(key, value)

        if exists_in_dst:
            result.overwritten.append(key)
        else:
            result.promoted.append(key)

    dst_vault.save()
    return result
