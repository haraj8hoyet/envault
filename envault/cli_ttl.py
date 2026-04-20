"""CLI commands for TTL management."""

import click
from envault.vault import Vault
from envault.ttl import set_ttl, get_ttl, clear_ttl, purge_expired, TTLError


@click.group(name="ttl")
def ttl_cli():
    """Manage TTL (time-to-live) for vault variables."""


@ttl_cli.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("seconds", type=int)
@click.password_option("--password", "-p", prompt="Vault password")
def ttl_set(vault_name, key, seconds, password):
    """Set a TTL on KEY in VAULT_NAME (expires after SECONDS seconds)."""
    try:
        vault = Vault.open(vault_name, password)
        set_ttl(vault, key, seconds)
        vault.save()
        click.echo(f"TTL of {seconds}s set on '{key}'.")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ttl_cli.command("get")
@click.argument("vault_name")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password")
def ttl_get(vault_name, key, password):
    """Show remaining TTL for KEY in VAULT_NAME."""
    try:
        vault = Vault.open(vault_name, password)
        remaining = get_ttl(vault, key)
        if remaining is None:
            click.echo(f"No TTL set on '{key}'.")
        elif remaining <= 0:
            click.echo(f"'{key}' has expired.")
        else:
            click.echo(f"{remaining:.1f}s remaining on '{key}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ttl_cli.command("clear")
@click.argument("vault_name")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password")
def ttl_clear(vault_name, key, password):
    """Remove TTL from KEY in VAULT_NAME."""
    try:
        vault = Vault.open(vault_name, password)
        clear_ttl(vault, key)
        vault.save()
        click.echo(f"TTL cleared from '{key}'.")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ttl_cli.command("purge")
@click.argument("vault_name")
@click.password_option("--password", "-p", prompt="Vault password")
def ttl_purge(vault_name, password):
    """Delete all expired keys from VAULT_NAME."""
    try:
        vault = Vault.open(vault_name, password)
        purged = purge_expired(vault)
        vault.save()
        if purged:
            click.echo(f"Purged {len(purged)} expired key(s): {', '.join(purged)}")
        else:
            click.echo("No expired keys found.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
