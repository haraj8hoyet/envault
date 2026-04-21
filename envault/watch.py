"""Watch a vault for changes and trigger shell hooks or notifications."""

import time
import hashlib
import json
from pathlib import Path
from typing import Callable, Optional

from envault.storage import _vault_path, vault_exists


class WatchError(Exception):
    pass


def _vault_checksum(vault_name: str, password: str) -> str:
    """Return a checksum representing the current state of the vault."""
    from envault.vault import Vault

    v = Vault.open(vault_name, password)
    keys = sorted(v.keys())
    snapshot = {k: v.get(k) for k in keys}
    serialized = json.dumps(snapshot, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()


def watch_vault(
    vault_name: str,
    password: str,
    on_change: Callable[[str, str], None],
    interval: float = 2.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll a vault and call on_change(vault_name, new_checksum) when it changes.

    Args:
        vault_name: Name of the vault to watch.
        password: Password to open the vault.
        on_change: Callback invoked with (vault_name, new_checksum) on change.
        interval: Polling interval in seconds.
        max_iterations: Stop after this many iterations (None = run forever).
    """
    if not vault_exists(vault_name):
        raise WatchError(f"Vault '{vault_name}' does not exist.")

    last_checksum = _vault_checksum(vault_name, password)
    iterations = 0

    while max_iterations is None or iterations < max_iterations:
        time.sleep(interval)
        try:
            current = _vault_checksum(vault_name, password)
        except Exception as exc:
            raise WatchError(f"Error reading vault during watch: {exc}") from exc

        if current != last_checksum:
            last_checksum = current
            on_change(vault_name, current)

        iterations += 1


def diff_checksum(old: str, new: str) -> bool:
    """Return True if two checksums differ (i.e. vault changed)."""
    return old != new
