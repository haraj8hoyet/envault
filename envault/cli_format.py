"""CLI commands for formatting vault variable keys and values."""

import click
from envault.vault import Vault
from envault.storage import vault_exists
from envault.env_format import format_vault


@click.group(name="format")
def format_cli():
    """Format and normalize vault variable keys and values."""


@format_cli.command(name="run")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--no-normalize-keys", is_flag=True, default=False, help="Skip key normalization.")
@click.option("--no-strip-values", is_flag=True, default=False, help="Skip value stripping.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without applying them.")
def format_run(vault_name, password, no_normalize_keys, no_strip_values, dry_run):
    """Format keys and values in a vault."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    try:
        vault = Vault.open(vault_name, password)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    result = format_vault(
        vault,
        normalize_keys=not no_normalize_keys,
        strip_values=not no_strip_values,
        dry_run=dry_run,
    )

    if dry_run:
        click.echo("[dry-run] No changes applied.")

    if not result.has_changes:
        click.echo("Nothing to format. All variables are already clean.")
        return

    click.echo(result.summary())

    if not dry_run:
        vault.save()
        click.echo("Vault saved.")
