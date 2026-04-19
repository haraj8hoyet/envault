"""Command-line interface for envault."""

import sys
import click
from envault.vault import Vault


@click.group()
def cli():
    """envault — securely store and sync environment variables."""
    pass


@cli.command()
@click.argument("name")
@click.password_option(prompt="Master password", help="Master password for the vault.")
def create(name, password):
    """Create a new vault with the given NAME."""
    try:
        Vault.create(name, password)
        click.echo(f"Vault '{name}' created successfully.")
    except FileExistsError:
        click.echo(f"Error: Vault '{name}' already exists.", err=True)
        sys.exit(1)


@cli.command(name="set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def set_var(vault_name, key, value, password):
    """Set KEY=VALUE in the specified vault."""
    try:
        vault = Vault.open(vault_name, password)
        vault.set(key, value)
        click.echo(f"Set '{key}' in vault '{vault_name}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="get")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def get_var(vault_name, key, password):
    """Get the value of KEY from the specified vault."""
    try:
        vault = Vault.open(vault_name, password)
        value = vault.get(key)
        if value is None:
            click.echo(f"Key '{key}' not found.", err=True)
            sys.exit(1)
        click.echo(value)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="list")
@click.argument("vault_name")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def list_vars(vault_name, password):
    """List all keys stored in the specified vault."""
    try:
        vault = Vault.open(vault_name, password)
        keys = vault.keys()
        if not keys:
            click.echo("(no variables stored)")
        else:
            for key in sorted(keys):
                click.echo(key)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("vault_name")
@click.password_option(prompt="Master password", confirmation_prompt=False)
def export(vault_name, password):
    """Export all variables as shell export statements."""
    try:
        vault = Vault.open(vault_name, password)
        for key in sorted(vault.keys()):
            value = vault.get(key)
            click.echo(f"export {key}={value!r}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
