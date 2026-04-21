"""Backup and restore vault archives (zip-based)."""

import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from envault.storage import _vault_path, vault_exists


class BackupError(Exception):
    pass


def _default_backup_dir() -> Path:
    return Path.home() / ".envault" / "backups"


def create_backup(vault_name: str, dest_dir: Path | None = None) -> Path:
    """Archive the encrypted vault file into a timestamped zip."""
    if not vault_exists(vault_name):
        raise BackupError(f"Vault '{vault_name}' does not exist.")

    dest_dir = dest_dir or _default_backup_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    zip_name = f"{vault_name}_{ts}.evbak"
    zip_path = dest_dir / zip_name

    vault_file = _vault_path(vault_name)
    meta = {"vault": vault_name, "created_at": ts, "source": str(vault_file)}

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(vault_file, arcname="vault.enc")
        zf.writestr("meta.json", json.dumps(meta, indent=2))

    return zip_path


def list_backups(vault_name: str, backup_dir: Path | None = None) -> list[dict]:
    """Return metadata for all backups of a given vault, newest first."""
    backup_dir = backup_dir or _default_backup_dir()
    if not backup_dir.exists():
        return []

    results = []
    for f in backup_dir.glob(f"{vault_name}_*.evbak"):
        try:
            with zipfile.ZipFile(f, "r") as zf:
                meta = json.loads(zf.read("meta.json"))
                meta["filename"] = f.name
                meta["path"] = str(f)
                results.append(meta)
        except Exception:
            continue

    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return results


def restore_backup(backup_path: Path, vault_name: str | None = None) -> str:
    """Restore a vault from a backup archive."""
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise BackupError(f"Backup file not found: {backup_path}")

    with zipfile.ZipFile(backup_path, "r") as zf:
        meta = json.loads(zf.read("meta.json"))
        target_vault = vault_name or meta["vault"]
        dest = _vault_path(target_vault)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zf.open("vault.enc") as src, open(dest, "wb") as dst:
            dst.write(src.read())

    return target_vault


def delete_backup(backup_path: Path) -> None:
    """Delete a specific backup file."""
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise BackupError(f"Backup not found: {backup_path}")
    backup_path.unlink()
