"""Audit log for vault operations."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _audit_path(vault_name: str, base_dir: Optional[str] = None) -> Path:
    if base_dir is None:
        base_dir = os.environ.get("ENVAULT_DIR", str(Path.home() / ".envault"))
    return Path(base_dir) / vault_name / "audit.log"


def record_event(vault_name: str, action: str, key: Optional[str] = None, base_dir: Optional[str] = None) -> None:
    """Append an audit event to the vault's audit log."""
    path = _audit_path(vault_name, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
    }
    if key is not None:
        event["key"] = key
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")


def read_events(vault_name: str, base_dir: Optional[str] = None) -> List[dict]:
    """Return all audit events for a vault."""
    path = _audit_path(vault_name, base_dir)
    if not path.exists():
        return []
    events = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def clear_audit_log(vault_name: str, base_dir: Optional[str] = None) -> None:
    """Clear the audit log for a vault."""
    path = _audit_path(vault_name, base_dir)
    if path.exists():
        path.unlink()
