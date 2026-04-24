"""Validate vault variables against a schema of required keys and patterns."""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationIssue:
    key: str
    reason: str
    severity: str = "error"  # "error" or "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.reason}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def validate_vault(
    vault,
    required_keys: Optional[List[str]] = None,
    patterns: Optional[Dict[str, str]] = None,
    allow_empty: bool = False,
) -> ValidationResult:
    """Validate vault contents against required keys and regex patterns.

    Args:
        vault: Vault instance with .keys() and .get(key) methods.
        required_keys: Keys that must exist in the vault.
        patterns: Mapping of key -> regex pattern the value must match.
        allow_empty: If False, empty string values produce a warning.

    Returns:
        ValidationResult with collected issues.
    """
    result = ValidationResult()
    existing_keys = set(vault.keys())

    for key in required_keys or []:
        if key not in existing_keys:
            result.issues.append(ValidationIssue(key=key, reason="required key is missing", severity="error"))

    for key in existing_keys:
        value = vault.get(key)
        if not allow_empty and value == "":
            result.issues.append(ValidationIssue(key=key, reason="value is empty", severity="warning"))

        if patterns and key in patterns:
            pattern = patterns[key]
            if not re.fullmatch(pattern, value or ""):
                result.issues.append(
                    ValidationIssue(
                        key=key,
                        reason=f"value does not match pattern '{pattern}'",
                        severity="error",
                    )
                )

    return result
