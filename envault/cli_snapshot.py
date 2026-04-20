"""CLI commands for managing vault snapshots."""

import click
from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    SnapshotError,
)


@click.group(name="snapshot")
def snapshot_cli():
    """Manage vault snapshots (backup and restore)."""
    pass


@snapshot_cli.command(name="create")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--label", default=None, help="Optional label for the snapshot.")
def snapshot_create(vault_name, password, label):
    """Create a snapshot of a vault."""
    try:
        filename = create_snapshot(vault_name, password, label=label)
        click.echo(f"Snapshot created: {filename}")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cli.command(name="list")
@click.argument("vault_name")
def snapshot_list(vault_name):
    """List all snapshots for a vault."""
    try:
        snapshots = list_snapshots(vault_name)
        if not snapshots:
            click.echo(f"No snapshots found for vault '{vault_name}'.")
            return
        click.echo(f"Snapshots for '{vault_name}':")
        for snap in snapshots:
            label_part = f"  [{snap['label']}]" if snap.get("label") else ""
            click.echo(f"  {snap['filename']}{label_part}  ({snap['created_at']})")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cli.command(name="restore")
@click.argument("vault_name")
@click.argument("snapshot_filename")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--new-password",
    default=None,
    help="Set a new password when restoring (defaults to original password).",
)
def snapshot_restore(vault_name, snapshot_filename, password, new_password):
    """Restore a vault from a snapshot."""
    try:
        restore_snapshot(
            vault_name,
            snapshot_filename,
            password,
            new_password=new_password,
        )
        click.echo(f"Vault '{vault_name}' restored from snapshot '{snapshot_filename}'.")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cli.command(name="delete")
@click.argument("vault_name")
@click.argument("snapshot_filename")
@click.confirmation_option(prompt="Are you sure you want to delete this snapshot?")
def snapshot_delete(vault_name, snapshot_filename):
    """Delete a specific snapshot."""
    try:
        delete_snapshot(vault_name, snapshot_filename)
        click.echo(f"Snapshot '{snapshot_filename}' deleted.")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
