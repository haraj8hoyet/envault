"""CLI commands for syncing vault variables with the OS environment."""

from __future__ import annotations

import click

from envault.storage import vault_exists
from envault.vault import Vault
from envault.env_sync import load_into_env, export_from_env, SyncError


@click.group(name="sync")
def sync_cli() -> None:
    """Sync vault variables with the OS environment."""


@sync_cli.command("load")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--keys", "-k", multiple=True, help="Specific keys to load (default: all)")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing env vars")
def sync_load(vault_name: str, password: str, keys: tuple, overwrite: bool) -> None:
    """Load vault variables into the current shell environment (prints export statements)."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    try:
        vault = Vault.open(vault_name, password)
        result = load_into_env(vault, list(keys) or None, overwrite=overwrite)
    except SyncError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    for key in result.loaded:
        click.echo(f"export {key}={vault.get(key)!r}")

    click.echo(f"# {result.summary()}", err=True)


@sync_cli.command("push")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--keys", "-k", multiple=True, help="Specific env vars to push (default: all)")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vault keys")
def sync_push(vault_name: str, password: str, keys: tuple, overwrite: bool) -> None:
    """Push current environment variables into the vault."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    try:
        vault = Vault.open(vault_name, password)
        result = export_from_env(vault, list(keys) or None, overwrite=overwrite)
        vault.save()
    except SyncError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    for key in result.exported:
        click.echo(f"  pushed: {key}")
    for key in result.skipped:
        click.echo(f"  skipped (exists): {key}")

    click.echo(result.summary())
