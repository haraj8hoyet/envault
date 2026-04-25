"""CLI commands for group-based variable management."""

import click

from envault.vault import Vault
from envault.storage import vault_exists
from envault.env_group import (
    GroupError,
    set_group,
    remove_group,
    list_groups,
    keys_in_group,
    rename_group,
)


@click.group("group")
def group_cli():
    """Manage variable groups within a vault."""


@group_cli.command("assign")
@click.argument("vault_name")
@click.argument("key")
@click.argument("group")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def group_assign(vault_name: str, key: str, group: str, password: str):
    """Assign KEY to GROUP in VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        v = Vault.open(vault_name, password)
        set_group(v, key, group)
        v.save()
        click.echo(f"Key '{key}' assigned to group '{group}'.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@group_cli.command("unassign")
@click.argument("vault_name")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def group_unassign(vault_name: str, key: str, password: str):
    """Remove group assignment from KEY in VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        v = Vault.open(vault_name, password)
        remove_group(v, key)
        v.save()
        click.echo(f"Group assignment removed from '{key}'.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@group_cli.command("list")
@click.argument("vault_name")
@click.option("--group", default=None, help="Filter by group name.")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def group_list(vault_name: str, group: str, password: str):
    """List groups (and their keys) in VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    v = Vault.open(vault_name, password)
    if group:
        keys = keys_in_group(v, group)
        if not keys:
            click.echo(f"No keys in group '{group}'.")
        else:
            for k in sorted(keys):
                click.echo(f"  {k}")
    else:
        groups = list_groups(v)
        if not groups:
            click.echo("No groups defined.")
        else:
            for grp, keys in sorted(groups.items()):
                click.echo(f"[{grp}]")
                for k in sorted(keys):
                    click.echo(f"  {k}")


@group_cli.command("rename")
@click.argument("vault_name")
@click.argument("old_name")
@click.argument("new_name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def group_rename(vault_name: str, old_name: str, new_name: str, password: str):
    """Rename a group from OLD_NAME to NEW_NAME in VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        v = Vault.open(vault_name, password)
        count = rename_group(v, old_name, new_name)
        v.save()
        click.echo(f"Renamed group '{old_name}' -> '{new_name}' ({count} key(s) updated).")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
