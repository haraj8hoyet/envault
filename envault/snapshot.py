"""Snapshot support: capture and restore vault state at a point in time."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

from envault.vault import Vault


class SnapshotError(Exception):
    pass


def _snapshot_dir(vault_name: str) -> Path:
    from envault.storage import _vault_path
    base = _vault_path(vault_name).parent / "snapshots"
    base.mkdir(parents=True, exist_ok=True)
    return base


def create_snapshot(vault_name: str, password: str, label: Optional[str] = None) -> str:
    """Capture current vault contents and save as a snapshot.
    Returns the snapshot filename."""
    vault = Vault.open(vault_name, password)
    data = {key: vault.get(key) for key in vault.keys()}
    timestamp = int(time.time())
    label_part = f"_{label}" if label else ""
    filename = f"{timestamp}{label_part}.json"
    snapshot_path = _snapshot_dir(vault_name) / filename
    snapshot_path.write_text(
        json.dumps({"timestamp": timestamp, "label": label, "data": data}, indent=2)
    )
    return filename


def list_snapshots(vault_name: str) -> List[dict]:
    """Return metadata for all snapshots of a vault, newest first."""
    snap_dir = _snapshot_dir(vault_name)
    snapshots = []
    for path in sorted(snap_dir.glob("*.json"), reverse=True):
        try:
            meta = json.loads(path.read_text())
            snapshots.append({
                "filename": path.name,
                "timestamp": meta.get("timestamp"),
                "label": meta.get("label"),
                "keys": len(meta.get("data", {})),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return snapshots


def restore_snapshot(vault_name: str, password: str, filename: str) -> int:
    """Restore vault to the state captured in a snapshot.
    Returns the number of variables restored."""
    snap_path = _snapshot_dir(vault_name) / filename
    if not snap_path.exists():
        raise SnapshotError(f"Snapshot not found: {filename}")
    try:
        meta = json.loads(snap_path.read_text())
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"Corrupt snapshot file: {filename}") from exc
    vault = Vault.open(vault_name, password)
    for key, value in meta["data"].items():
        vault.set(key, value)
    vault.save()
    return len(meta["data"])


def delete_snapshot(vault_name: str, filename: str) -> None:
    """Delete a snapshot file."""
    snap_path = _snapshot_dir(vault_name) / filename
    if not snap_path.exists():
        raise SnapshotError(f"Snapshot not found: {filename}")
    snap_path.unlink()
