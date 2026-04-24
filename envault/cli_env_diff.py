"""CLI commands for diffing vault contents against the live environment."""
from __future__ import annotations

import os

import click

from envault.env_diff import diff_env
from envault.storage import vault_exists
from envault.vault import Vault


@click.group(name="env-diff")
def env_diff_cli() -> None:
    """Compare vault variables against the current environment."""


@env_diff_cli.command("run")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--include-extra",
    is_flag=True,
    default=False,
    help="Also report keys present in env but not in vault.",
)
@click.option(
    "--only-diff",
    is_flag=True,
    default=False,
    help="Suppress matching keys from output.",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 when differences are found.",
)
def env_diff_run(
    vault_name: str,
    password: str,
    include_extra: bool,
    only_diff: bool,
    exit_code: bool,
) -> None:
    """Diff VAULT_NAME variables against the current process environment."""
    if not vault_exists(vault_name):
        raise click.ClickException(f"Vault '{vault_name}' not found.")

    try:
        vault = Vault.open(vault_name, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Could not open vault: {exc}") from exc

    result = diff_env(vault, dict(os.environ), include_extra=include_extra)

    if not result.entries:
        click.echo("No keys to compare.")
        return

    for entry in result.entries:
        if only_diff and entry.status == "match":
            continue
        click.echo(str(entry))

    click.echo(f"\nSummary: {result.summary()}")

    if exit_code and result.has_differences:
        raise SystemExit(1)
