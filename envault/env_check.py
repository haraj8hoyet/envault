"""Check vault variables against the current environment."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import os

from envault.vault import Vault


@dataclass
class CheckIssue:
    key: str
    kind: str  # 'missing' | 'mismatch' | 'extra'
    vault_value: Optional[str] = None
    env_value: Optional[str] = None

    def __str__(self) -> str:
        if self.kind == "missing":
            return f"[MISSING]  {self.key!r} is in vault but not set in environment"
        if self.kind == "mismatch":
            return f"[MISMATCH] {self.key!r} differs (vault != env)"
        if self.kind == "extra":
            return f"[EXTRA]    {self.key!r} is in environment but not in vault"
        return f"[UNKNOWN]  {self.key!r}"


@dataclass
class CheckResult:
    issues: List[CheckIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)

    def by_kind(self, kind: str) -> List[CheckIssue]:
        return [i for i in self.issues if i.kind == kind]


def check_vault_against_env(
    vault: Vault,
    *,
    report_extra: bool = False,
    keys: Optional[List[str]] = None,
) -> CheckResult:
    """Compare vault keys/values with os.environ.

    Args:
        vault: An open Vault instance.
        report_extra: If True, also report env vars not present in the vault.
        keys: Optional subset of keys to check; defaults to all vault keys.

    Returns:
        A CheckResult containing any discrepancies found.
    """
    result = CheckResult()
    vault_keys = keys if keys is not None else list(vault.keys())

    for key in vault_keys:
        vault_val = vault.get(key)
        env_val = os.environ.get(key)
        if env_val is None:
            result.issues.append(
                CheckIssue(key=key, kind="missing", vault_value=vault_val)
            )
        elif env_val != vault_val:
            result.issues.append(
                CheckIssue(
                    key=key,
                    kind="mismatch",
                    vault_value=vault_val,
                    env_value=env_val,
                )
            )

    if report_extra:
        vault_key_set = set(vault_keys)
        for env_key in os.environ:
            if env_key not in vault_key_set:
                result.issues.append(
                    CheckIssue(key=env_key, kind="extra", env_value=os.environ[env_key])
                )

    return result
