"""Format and normalize environment variable keys/values in a vault."""

from dataclasses import dataclass, field
from typing import List, Optional


class FormatError(Exception):
    pass


@dataclass
class FormatChange:
    key: str
    old_value: str
    new_value: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.reason}"


@dataclass
class FormatResult:
    changes: List[FormatChange] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        lines = [f"{len(self.changes)} change(s), {len(self.skipped)} skipped"]
        for c in self.changes:
            lines.append(f"  ~ {c}")
        return "\n".join(lines)


def normalize_key(key: str) -> str:
    """Uppercase and replace spaces/hyphens with underscores."""
    return key.strip().upper().replace(" ", "_").replace("-", "_")


def strip_value(value: str) -> str:
    """Strip leading/trailing whitespace from a value."""
    return value.strip()


def format_vault(
    vault,
    normalize_keys: bool = True,
    strip_values: bool = True,
    dry_run: bool = False,
) -> FormatResult:
    """Apply formatting rules to all variables in a vault."""
    result = FormatResult()

    for key in list(vault.keys()):
        original_value = vault.get(key)
        new_key = normalize_key(key) if normalize_keys else key
        new_value = strip_value(original_value) if strip_values else original_value

        key_changed = new_key != key
        value_changed = new_value != original_value

        if not key_changed and not value_changed:
            result.skipped.append(key)
            continue

        reason_parts = []
        if key_changed:
            reason_parts.append(f"key '{key}' -> '{new_key}'")
        if value_changed:
            reason_parts.append("value stripped")

        change = FormatChange(
            key=key,
            old_value=original_value,
            new_value=new_value,
            reason=", ".join(reason_parts),
        )
        result.changes.append(change)

        if not dry_run:
            if key_changed:
                vault.delete(key)
                vault.set(new_key, new_value)
            else:
                vault.set(key, new_value)

    return result
