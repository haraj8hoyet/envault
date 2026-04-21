"""CLI commands for vault backup and restore."""

import click
from pathlib import Path

from envault.backup import (
    BackupError,
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
)


@click.group("backup")
def backup_cli():
    """Backup and restore vault archives."""


@backup_cli.command("create")
@click.argument("vault_name")
@click.option("--dest", default=None, help="Directory to store the backup.")
def backup_create(vault_name: str, dest: str | None):
    """Create a backup archive of VAULT_NAME."""
    try:
        dest_dir = Path(dest) if dest else None
        path = create_backup(vault_name, dest_dir)
        click.echo(f"Backup created: {path}")
    except BackupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@backup_cli.command("list")
@click.argument("vault_name")
@click.option("--dir", "backup_dir", default=None, help="Directory to search.")
def backup_list(vault_name: str, backup_dir: str | None):
    """List backups for VAULT_NAME."""
    bdir = Path(backup_dir) if backup_dir else None
    backups = list_backups(vault_name, bdir)
    if not backups:
        click.echo(f"No backups found for '{vault_name}'.")
        return
    for b in backups:
        click.echo(f"{b['filename']}  ({b['created_at']})")


@backup_cli.command("restore")
@click.argument("backup_path")
@click.option("--vault", default=None, help="Override restored vault name.")
def backup_restore(backup_path: str, vault: str | None):
    """Restore a vault from BACKUP_PATH."""
    try:
        name = restore_backup(Path(backup_path), vault)
        click.echo(f"Vault '{name}' restored from {backup_path}")
    except BackupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@backup_cli.command("delete")
@click.argument("backup_path")
def backup_delete(backup_path: str):
    """Delete a backup archive."""
    try:
        delete_backup(Path(backup_path))
        click.echo(f"Deleted backup: {backup_path}")
    except BackupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
