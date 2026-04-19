"""Compare vault contents or show changes between vault and environment."""

from typing import Dict, List, Tuple, Optional
from envault.vault import Vault


class DiffResult:
    def __init__(
        self,
        added: Dict[str, str],
        removed: Dict[str, str],
        changed: Dict[str, Tuple[str, str]],
        unchanged: List[str],
    ):
        self.added = added
        self.removed = removed
        self.changed = changed
        self.unchanged = unchanged

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_dicts(old: Dict[str, str], new: Dict[str, str]) -> DiffResult:
    """Compare two dicts and return a DiffResult."""
    old_keys = set(old)
    new_keys = set(new)

    added = {k: new[k] for k in new_keys - old_keys}
    removed = {k: old[k] for k in old_keys - new_keys}
    changed = {
        k: (old[k], new[k])
        for k in old_keys & new_keys
        if old[k] != new[k]
    }
    unchanged = [k for k in old_keys & new_keys if old[k] == new[k]]

    return DiffResult(added=added, removed=removed, changed=changed, unchanged=unchanged)


def diff_vaults(
    vault_a: Vault,
    vault_b: Vault,
) -> DiffResult:
    """Diff two open Vault instances."""
    data_a = {k: vault_a.get(k) for k in vault_a.keys()}
    data_b = {k: vault_b.get(k) for k in vault_b.keys()}
    return diff_dicts(data_a, data_b)


def diff_vault_env(
    vault: Vault,
    env: Optional[Dict[str, str]] = None,
) -> DiffResult:
    """Diff vault contents against a dict (defaults to os.environ)."""
    import os
    env_data = env if env is not None else dict(os.environ)
    vault_data = {k: vault.get(k) for k in vault.keys()}
    # Only compare keys present in the vault
    filtered_env = {k: env_data[k] for k in vault_data if k in env_data}
    missing_in_env = {k: vault_data[k] for k in vault_data if k not in env_data}

    result = diff_dicts(vault_data, filtered_env)
    # Keys in vault but not in env count as removed from env perspective
    result.removed.update(missing_in_env)
    return result
