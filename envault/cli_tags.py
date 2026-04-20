"""CLI commands for managing variable tags."""

from __future__ import annotations

import click

from envault.vault import Vault
from envault.tags import add_tag, remove_tag, list_by_tag, all_tags, TagError


@click.group(name="tag")
def tag_cli():
    """Manage tags on vault variables."""


@tag_cli.command("add")
@click.argument("vault_name")
@click.argument("key")
@click.argument("tag")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def tag_add(vault_name: str, key: str, tag: str, password: str):
    """Add TAG to KEY in VAULT_NAME."""
    try:
        vault = Vault.open(vault_name, password)
        updated = add_tag(vault, key, tag)
        click.echo(f"Tag '{tag}' added to '{key}'. Tags: {', '.join(updated)}")
    except (TagError, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@tag_cli.command("remove")
@click.argument("vault_name")
@click.argument("key")
@click.argument("tag")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def tag_remove(vault_name: str, key: str, tag: str, password: str):
    """Remove TAG from KEY in VAULT_NAME."""
    try:
        vault = Vault.open(vault_name, password)
        updated = remove_tag(vault, key, tag)
        remaining = ', '.join(updated) if updated else '(none)'
        click.echo(f"Tag '{tag}' removed from '{key}'. Remaining tags: {remaining}")
    except (TagError, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@tag_cli.command("list")
@click.argument("vault_name")
@click.option("--tag", default=None, help="Filter keys by this tag.")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def tag_list(vault_name: str, tag: str | None, password: str):
    """List tags for all keys, or filter by TAG."""
    try:
        vault = Vault.open(vault_name, password)
        if tag:
            keys = list_by_tag(vault, tag)
            if keys:
                click.echo(f"Keys tagged '{tag}':")
                for k in keys:
                    click.echo(f"  {k}")
            else:
                click.echo(f"No keys found with tag '{tag}'.")
        else:
            mapping = all_tags(vault)
            if mapping:
                for k, tags in sorted(mapping.items()):
                    click.echo(f"  {k}: {', '.join(tags)}")
            else:
                click.echo("No tags defined.")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
