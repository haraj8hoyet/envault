"""CLI commands for managing profiles."""

import click
from envault.profile import (
    ProfileError,
    create_profile,
    delete_profile,
    get_profile,
    list_profiles,
    update_profile,
)


@click.group(name="profile")
def profile_cli():
    """Manage vault profiles (named groups of vaults)."""


@profile_cli.command("create")
@click.argument("name")
@click.argument("vaults", nargs=-1, required=True)
def profile_create(name, vaults):
    """Create a new profile with one or more vault names."""
    try:
        create_profile(name, list(vaults))
        click.echo(f"Profile '{name}' created with vaults: {', '.join(vaults)}")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profile_cli.command("list")
def profile_list():
    """List all profiles."""
    names = list_profiles()
    if not names:
        click.echo("No profiles found.")
        return
    for name in names:
        click.echo(name)


@profile_cli.command("show")
@click.argument("name")
def profile_show(name):
    """Show vaults in a profile."""
    try:
        data = get_profile(name)
        vaults = data.get("vaults", [])
        click.echo(f"Profile '{name}':")
        for v in vaults:
            click.echo(f"  - {v}")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profile_cli.command("update")
@click.argument("name")
@click.argument("vaults", nargs=-1, required=True)
def profile_update(name, vaults):
    """Replace vault list for an existing profile."""
    try:
        update_profile(name, list(vaults))
        click.echo(f"Profile '{name}' updated.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profile_cli.command("delete")
@click.argument("name")
def profile_delete(name):
    """Delete a profile."""
    try:
        delete_profile(name)
        click.echo(f"Profile '{name}' deleted.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
