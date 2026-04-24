"""Sync vault variables to/from the current OS environment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import Vault


class SyncError(Exception):
    """Raised when a sync operation fails."""


@dataclass
class SyncResult:
    loaded: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    exported: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = []
        if self.loaded:
            parts.append(f"loaded {len(self.loaded)} key(s) into environment")
        if self.skipped:
            parts.append(f"skipped {len(self.skipped)} existing key(s)")
        if self.exported:
            parts.append(f"exported {len(self.exported)} key(s) from environment")
        return "; ".join(parts) if parts else "nothing to sync"


def load_into_env(
    vault: Vault,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> SyncResult:
    """Load vault variables into the current process environment."""
    result = SyncResult()
    target_keys = keys if keys is not None else vault.keys()

    for key in target_keys:
        if not vault.has(key):
            raise SyncError(f"Key '{key}' not found in vault")
        if key in os.environ and not overwrite:
            result.skipped.append(key)
        else:
            os.environ[key] = vault.get(key)
            result.loaded.append(key)

    return result


def export_from_env(
    vault: Vault,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> SyncResult:
    """Write current OS environment variables into the vault."""
    result = SyncResult()
    target_keys = keys if keys is not None else list(os.environ.keys())

    for key in target_keys:
        if key not in os.environ:
            raise SyncError(f"Environment variable '{key}' is not set")
        if vault.has(key) and not overwrite:
            result.skipped.append(key)
        else:
            vault.set(key, os.environ[key])
            result.exported.append(key)

    return result
