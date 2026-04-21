"""CLI commands for PIN management."""

import click
from envault.pin import set_pin, verify_pin, clear_pin, has_pin, PinError
from envault.storage import vault_exists


@click.group(name="pin")
def pin_cli():
    """Manage quick-unlock PINs for vaults."""


@pin_cli.command("set")
@click.argument("vault_name")
@click.password_option("--password", prompt="Vault password", help="Master password for the vault.")
@click.option("--pin", prompt="New PIN", hide_input=True, confirmation_prompt=True, help="PIN to set (min 4 chars).")
def pin_set(vault_name: str, password: str, pin: str):
    """Set a PIN for quick-unlock of VAULT_NAME."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)
    try:
        set_pin(vault_name, password, pin)
        click.echo(f"PIN set for vault '{vault_name}'.")
    except PinError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@pin_cli.command("verify")
@click.argument("vault_name")
@click.password_option("--password", prompt="Vault password", help="Master password for the vault.")
@click.option("--pin", prompt="PIN", hide_input=True, help="PIN to verify.")
def pin_verify(vault_name: str, password: str, pin: str):
    """Verify a PIN against VAULT_NAME."""
    try:
        ok = verify_pin(vault_name, password, pin)
        if ok:
            click.echo("PIN is valid.")
        else:
            click.echo("PIN is invalid.", err=True)
            raise SystemExit(1)
    except PinError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@pin_cli.command("clear")
@click.argument("vault_name")
@click.confirmation_option(prompt="Remove PIN for this vault?")
def pin_clear(vault_name: str):
    """Remove the PIN for VAULT_NAME."""
    if not has_pin(vault_name):
        click.echo(f"No PIN configured for vault '{vault_name}'.")
        return
    clear_pin(vault_name)
    click.echo(f"PIN cleared for vault '{vault_name}'.")


@pin_cli.command("status")
@click.argument("vault_name")
def pin_status(vault_name: str):
    """Show whether a PIN is configured for VAULT_NAME."""
    if has_pin(vault_name):
        click.echo(f"PIN is configured for vault '{vault_name}'.")
    else:
        click.echo(f"No PIN configured for vault '{vault_name}'.")
