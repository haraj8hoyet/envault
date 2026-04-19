"""CLI commands for importing variables into a vault."""

import click
from envault.vault import Vault
from envault.import_vars import import_from_file, import_from_env


@click.group()
def import_cli():
    """Import environment variables into a vault."""
    pass


@import_cli.command("file")
@click.argument("vault_name")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["dotenv", "json", "shell"]),
    default=None,
    help="File format (auto-detected if omitted)",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
def import_file(vault_name, filepath, password, fmt, overwrite):
    """Import variables from a file into VAULT_NAME."""
    try:
        vault = Vault.open(vault_name, password)
    except Exception as e:
        raise click.ClickException(str(e))

    try:
        variables = import_from_file(filepath, fmt=fmt)
    except Exception as e:
        raise click.ClickException(f"Failed to parse file: {e}")

    imported = 0
    skipped = 0
    for key, value in variables.items():
        if not overwrite and vault.get(key) is not None:
            skipped += 1
            continue
        vault.set(key, value)
        imported += 1

    click.echo(f"Imported {imported} variable(s) into '{vault_name}'" +
               (f", skipped {skipped} existing" if skipped else "."))


@import_cli.command("env")
@click.argument("vault_name")
@click.argument("keys", nargs=-1)
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
def import_env(vault_name, keys, password, overwrite):
    """Import variables from the current environment into VAULT_NAME."""
    try:
        vault = Vault.open(vault_name, password)
    except Exception as e:
        raise click.ClickException(str(e))

    variables = import_from_env(keys=list(keys) if keys else None)

    imported = 0
    skipped = 0
    for key, value in variables.items():
        if not overwrite and vault.get(key) is not None:
            skipped += 1
            continue
        vault.set(key, value)
        imported += 1

    click.echo(f"Imported {imported} variable(s) into '{vault_name}'" +
               (f", skipped {skipped} existing" if skipped else "."))
