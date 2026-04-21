"""CLI commands for watching vault changes."""

import click
from envault.storage import vault_exists
from envault.watch import watch_vault, WatchError


@click.group(name="watch")
def watch_cli():
    """Watch a vault for changes."""


@watch_cli.command(name="start")
@click.argument("vault_name")
@click.password_option("--password", "-p", prompt="Vault password", help="Vault password.")
@click.option(
    "--interval",
    "-i",
    default=2.0,
    show_default=True,
    type=float,
    help="Polling interval in seconds.",
)
@click.option(
    "--command",
    "-c",
    default=None,
    help="Shell command to run on change (receives VAULT_NAME and CHECKSUM env vars).",
)
def watch_start(vault_name: str, password: str, interval: float, command: str):
    """Watch VAULT_NAME and react to changes."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Watching vault '{vault_name}' every {interval}s. Press Ctrl+C to stop.")

    def on_change(name: str, checksum: str):
        click.echo(f"[change] {name} updated (checksum: {checksum[:12]}...)")
        if command:
            import subprocess
            import os

            env = {**os.environ, "VAULT_NAME": name, "CHECKSUM": checksum}
            subprocess.run(command, shell=True, env=env)

    try:
        watch_vault(vault_name, password, on_change=on_change, interval=interval)
    except WatchError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
