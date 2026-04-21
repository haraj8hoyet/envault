"""CLI commands for viewing key change history."""

from __future__ import annotations

import click

from envault.history import (
    get_history,
    clear_history,
    list_keys_with_history,
    HistoryError,
)
from envault.vault import Vault
from envault.storage import vault_exists


@click.group(name="history")
def history_cli() -> None:
    """Commands for inspecting key change history."""


@history_cli.command("show")
@click.argument("vault_name")
@click.argument("key")
@click.option("--limit", default=10, show_default=True, help="Max entries to display.")
def history_show(vault_name: str, key: str, limit: int) -> None:
    """Show change history for a key in a vault."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    entries = get_history(vault_name, key)
    if not entries:
        click.echo(f"No history found for key '{key}'.")
        return

    for entry in entries[-limit:]:
        actor = entry.get("actor", "unknown")
        click.echo(f"[{entry['timestamp']}] {entry['key']} = {entry['value']!r}  (by {actor})")


@history_cli.command("list")
@click.argument("vault_name")
def history_list(vault_name: str) -> None:
    """List all keys that have recorded history in a vault."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    keys = list_keys_with_history(vault_name)
    if not keys:
        click.echo("No history records found.")
        return
    for k in keys:
        click.echo(k)


@history_cli.command("clear")
@click.argument("vault_name")
@click.argument("key")
@click.confirmation_option(prompt="Clear history for this key?")
def history_clear(vault_name: str, key: str) -> None:
    """Delete history records for a specific key."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    clear_history(vault_name, key)
    click.echo(f"History cleared for '{key}'.")
