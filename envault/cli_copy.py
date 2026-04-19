"""CLI commands for copying variables between vaults."""

import click
from envault.copy import copy_variable, copy_all, copy_variables, CopyError
from envault.storage import vault_exists


@click.group(name="copy")
def copy_cli():
    """Copy variables between vaults."""
    pass


@copy_cli.command(name="var")
@click.argument("src_vault")
@click.argument("dst_vault")
@click.argument("key")
@click.option("--src-password", prompt=True, hide_input=True, help="Source vault password")
@click.option("--dst-password", prompt=True, hide_input=True, help="Destination vault password")
@click.option("--rename", default=None, help="New key name in destination vault")
def copy_var(src_vault, dst_vault, key, src_password, dst_password, rename):
    """Copy a single variable from SRC_VAULT to DST_VAULT."""
    for name in (src_vault, dst_vault):
        if not vault_exists(name):
            click.echo(f"Error: vault '{name}' does not exist.")
            raise SystemExit(1)
    try:
        target = copy_variable(src_vault, src_password, dst_vault, dst_password, key, new_key=rename)
        click.echo(f"Copied '{key}' -> '{target}' into vault '{dst_vault}'.")
    except CopyError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)


@copy_cli.command(name="all")
@click.argument("src_vault")
@click.argument("dst_vault")
@click.option("--src-password", prompt=True, hide_input=True, help="Source vault password")
@click.option("--dst-password", prompt=True, hide_input=True, help="Destination vault password")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys that already exist in destination")
def copy_all_cmd(src_vault, dst_vault, src_password, dst_password, no_overwrite):
    """Copy all variables from SRC_VAULT to DST_VAULT."""
    for name in (src_vault, dst_vault):
        if not vault_exists(name):
            click.echo(f"Error: vault '{name}' does not exist.")
            raise SystemExit(1)
    results = copy_all(src_vault, src_password, dst_vault, dst_password, overwrite=not no_overwrite)
    copied = sum(1 for v in results.values() if v == "copied")
    skipped = sum(1 for v in results.values() if v == "skipped")
    click.echo(f"Copied {copied} variable(s), skipped {skipped} variable(s).")
