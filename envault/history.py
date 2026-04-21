"""Track value change history for vault keys."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class HistoryError(Exception):
    pass


def _history_dir(vault_name: str) -> Path:
    base = Path(os.environ.get("ENVAULT_DIR", Path.home() / ".envault"))
    return base / "history" / vault_name


def _history_file(vault_name: str, key: str) -> Path:
    return _history_dir(vault_name) / f"{key}.jsonl"


def record_change(vault_name: str, key: str, new_value: str, actor: Optional[str] = None) -> None:
    """Append a history entry for a key change."""
    history_dir = _history_dir(vault_name)
    history_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "key": key,
        "value": new_value,
    }
    if actor:
        entry["actor"] = actor

    with _history_file(vault_name, key).open("a") as f:
        f.write(json.dumps(entry) + "\n")


def get_history(vault_name: str, key: str) -> List[dict]:
    """Return all recorded history entries for a key, oldest first."""
    path = _history_file(vault_name, key)
    if not path.exists():
        return []
    entries = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def clear_history(vault_name: str, key: str) -> None:
    """Delete history for a specific key."""
    path = _history_file(vault_name, key)
    if path.exists():
        path.unlink()


def list_keys_with_history(vault_name: str) -> List[str]:
    """Return keys that have history records in the vault."""
    d = _history_dir(vault_name)
    if not d.exists():
        return []
    return [p.stem for p in sorted(d.glob("*.jsonl"))]
