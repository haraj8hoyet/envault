"""CLI commands for searching vault variables."""
import click
from envault.vault import Vault
from envault.storage import vault_exists
from envault import search as search_mod


@click.group()
def search_cli():
    """Search and filter vault variables."""
    pass


@search_cli.command("keys")
@click.argument("vault_name")
@click.argument("pattern")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def search_keys(vault_name, pattern, password):
    """Search keys by glob PATTERN (e.g. 'DB_*')."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault = Vault.open(vault_name, password)
    results = search_mod.search_keys(vault, pattern)
    if not results:
        click.echo("No matching keys found.")
    else:
        for k, v in sorted(results.items()):
            click.echo(f"{k}={v}")


@search_cli.command("values")
@click.argument("vault_name")
@click.argument("substring")
@click.option("--case-sensitive", is_flag=True, default=False)
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def search_values(vault_name, substring, case_sensitive, password):
    """Search variables whose value contains SUBSTRING."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault = Vault.open(vault_name, password)
    results = search_mod.search_values(vault, substring, case_sensitive)
    if not results:
        click.echo("No matching variables found.")
    else:
        for k, v in sorted(results.items()):
            click.echo(f"{k}={v}")


@search_cli.command("prefix")
@click.argument("vault_name")
@click.argument("prefix")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def search_prefix(vault_name, prefix, password):
    """Return all variables whose key starts with PREFIX."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    vault = Vault.open(vault_name, password)
    results = search_mod.search_by_prefix(vault, prefix)
    if not results:
        click.echo("No matching keys found.")
    else:
        for k, v in sorted(results.items()):
            click.echo(f"{k}={v}")
