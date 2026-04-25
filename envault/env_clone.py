"""Clone a vault to a new vault, optionally filtering keys by prefix or pattern."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import Vault
from envault.storage import vault_exists


class CloneError(Exception):
    """Raised when a clone operation fails."""


@dataclass
class CloneResult:
    source: str
    destination: str
    copied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Cloned {len(self.copied)} key(s) from '{self.source}' "
            f"to '{self.destination}' ({len(self.skipped)} skipped)."
        )


def clone_vault(
    source_name: str,
    source_password: str,
    dest_name: str,
    dest_password: str,
    pattern: Optional[str] = None,
    overwrite: bool = False,
) -> CloneResult:
    """Clone variables from source vault into a new or existing destination vault.

    Args:
        source_name: Name of the vault to clone from.
        source_password: Password for the source vault.
        dest_name: Name of the destination vault.
        dest_password: Password for the destination vault.
        pattern: Optional glob pattern to filter keys (e.g. 'DB_*').
        overwrite: If True, overwrite existing keys in destination.

    Returns:
        CloneResult with lists of copied and skipped keys.

    Raises:
        CloneError: If source vault does not exist or passwords are wrong.
    """
    if not vault_exists(source_name):
        raise CloneError(f"Source vault '{source_name}' does not exist.")

    try:
        src = Vault.open(source_name, source_password)
    except Exception as exc:
        raise CloneError(f"Could not open source vault: {exc}") from exc

    if vault_exists(dest_name):
        try:
            dst = Vault.open(dest_name, dest_password)
        except Exception as exc:
            raise CloneError(f"Could not open destination vault: {exc}") from exc
    else:
        dst = Vault.create(dest_name, dest_password)

    result = CloneResult(source=source_name, destination=dest_name)

    for key in src.keys():
        if pattern and not fnmatch.fnmatch(key, pattern):
            result.skipped.append(key)
            continue
        if dst.has(key) and not overwrite:
            result.skipped.append(key)
            continue
        dst.set(key, src.get(key))
        result.copied.append(key)

    dst.save()
    return result
