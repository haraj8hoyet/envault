"""Compare vault contents against the current process environment."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvDiffEntry:
    key: str
    vault_value: Optional[str]
    env_value: Optional[str]
    status: str  # 'missing_in_env' | 'missing_in_vault' | 'mismatch' | 'match'

    def __str__(self) -> str:
        if self.status == "missing_in_env":
            return f"[MISSING IN ENV]  {self.key}  (vault={self.vault_value!r})"
        if self.status == "missing_in_vault":
            return f"[MISSING IN VAULT] {self.key}  (env={self.env_value!r})"
        if self.status == "mismatch":
            return f"[MISMATCH]         {self.key}  vault={self.vault_value!r}  env={self.env_value!r}"
        return f"[MATCH]            {self.key}"


@dataclass
class EnvDiffResult:
    entries: List[EnvDiffEntry] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return any(e.status != "match" for e in self.entries)

    def by_status(self, status: str) -> List[EnvDiffEntry]:
        return [e for e in self.entries if e.status == status]

    def summary(self) -> str:
        counts: Dict[str, int] = {}
        for e in self.entries:
            counts[e.status] = counts.get(e.status, 0) + 1
        parts = [f"{v} {k.replace('_', ' ')}" for k, v in counts.items()]
        return ", ".join(parts) if parts else "no entries"


def diff_env(
    vault,
    env: Dict[str, str],
    *,
    include_extra: bool = False,
) -> EnvDiffResult:
    """Diff vault keys against *env* dict (typically os.environ).

    Args:
        vault: open Vault instance.
        env: mapping to compare against (e.g. os.environ).
        include_extra: when True, report keys present in env but not vault.
    """
    result = EnvDiffResult()
    vault_keys = set(vault.keys())

    for key in sorted(vault_keys):
        vault_val = vault.get(key)
        if key not in env:
            result.entries.append(
                EnvDiffEntry(key, vault_val, None, "missing_in_env")
            )
        elif env[key] != vault_val:
            result.entries.append(
                EnvDiffEntry(key, vault_val, env[key], "mismatch")
            )
        else:
            result.entries.append(EnvDiffEntry(key, vault_val, env[key], "match"))

    if include_extra:
        for key in sorted(set(env.keys()) - vault_keys):
            result.entries.append(
                EnvDiffEntry(key, None, env[key], "missing_in_vault")
            )

    return result
