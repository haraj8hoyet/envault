"""Main CLI entry point for envault."""
import click
from envault.vault import Vault
from envault.storage import vault_exists, list_vaults
from envault.cli_import import import_cli
from envault.cli_search import search_cli


@click.group()
def cli():
    """envault — secure environment variable manager."""
    pass


@cli.command()
@click.argument("name")
@click.password_option()
def create(name, password):
    """Create a new vault."""
    if vault_exists(name):
        click.echo(f"Vault '{name}' already exists.", err=True)
        raise SystemExit(1)
    Vault.create(name, password)
    click.echo(f"Vault '{name}' created.")


@cli.command("set")
@click.argument("vault_name")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def set_var(vault_name, key, value, password):
    """Set a variable in a vault."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault = Vault.open(vault_name, password)
    vault.set(key, value)
    click.echo(f"Set {key} in '{vault_name}'.")


@cli.command("get")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def get_var(vault_name, key, password):
    """Get a variable from a vault."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault = Vault.open(vault_name, password)
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(value)


@cli.command("list")
@click.argument("vault_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def list_vars(vault_name, password):
    """List all variables in a vault."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault = Vault.open(vault_name, password)
    variables = vault.all()
    if not variables:
        click.echo("No variables stored.")
    else:
        for k, v in sorted(variables.items()):
            click.echo(f"{k}={v}")


@cli.command("vaults")
def vaults():
    """List all available vaults."""
    names = list_vaults()
    if not names:
        click.echo("No vaults found.")
    else:
        for name in sorted(names):
            click.echo(name)


cli.add_command(import_cli, name="import")
cli.add_command(search_cli, name="search")


if __name__ == "__main__":
    cli()
