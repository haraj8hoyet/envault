"""Lint vault variables for common issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    key: str
    severity: str  # 'error' | 'warning' | 'info'
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def lint_vault(vault) -> LintResult:
    """Run all lint checks against an open Vault and return a LintResult."""
    result = LintResult()

    for key in vault.keys():
        value = vault.get(key)

        # Error: empty value
        if value == "":
            result.issues.append(LintIssue(key, "error", "value is empty"))

        # Warning: key not uppercase
        if key != key.upper():
            result.issues.append(
                LintIssue(key, "warning", "key is not uppercase (convention)")
            )

        # Warning: key contains spaces
        if " " in key:
            result.issues.append(LintIssue(key, "error", "key contains spaces"))

        # Warning: value looks like an unresolved placeholder
        if value and value.startswith("<") and value.endswith(">"):
            result.issues.append(
                LintIssue(key, "warning", "value looks like an unfilled placeholder")
            )

        # Info: very long value
        if value and len(value) > 500:
            result.issues.append(
                LintIssue(key, "info", f"value is very long ({len(value)} chars)")
            )

    return result
