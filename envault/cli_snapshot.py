"""CLI commands for vault snapshot management."""

import click
from datetime import datetime

from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    SnapshotError,
)
from envault.storage import vault_exists


@click.group("snapshot")
def snapshot_cli():
    """Manage vault snapshots."""


@snapshot_cli.command("create")
@click.argument("vault_name")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.option("--label", "-l", default=None, help="Optional label for the snapshot.")
def snapshot_create(vault_name: str, password: str, label: str):
    """Create a snapshot of VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    try:
        filename = create_snapshot(vault_name, password, label=label)
        click.echo(f"Snapshot created: {filename}")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_cli.command("list")
@click.argument("vault_name")
def snapshot_list(vault_name: str):
    """List all snapshots for VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    snapshots = list_snapshots(vault_name)
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for snap in snapshots:
        ts = snap["timestamp"]
        dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "unknown"
        label = f" [{snap['label']}]" if snap["label"] else ""
        click.echo(f"{snap['filename']}{label}  {dt}  ({snap['keys']} keys)")


@snapshot_cli.command("restore")
@click.argument("vault_name")
@click.argument("filename")
@click.option("--password", "-p", prompt=True, hide_input=True)
def snapshot_restore(vault_name: str, filename: str, password: str):
    """Restore VAULT_NAME from a snapshot FILENAME."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    try:
        count = restore_snapshot(vault_name, password, filename)
        click.echo(f"Restored {count} variable(s) from '{filename}'.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_cli.command("delete")
@click.argument("vault_name")
@click.argument("filename")
@click.confirmation_option(prompt="Are you sure you want to delete this snapshot?")
def snapshot_delete(vault_name: str, filename: str):
    """Delete a snapshot FILENAME from VAULT_NAME."""
    try:
        delete_snapshot(vault_name, filename)
        click.echo(f"Snapshot '{filename}' deleted.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
