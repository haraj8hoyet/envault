"""CLI commands for checking vault variables against the current environment."""
from __future__ import annotations

import click

from envault.vault import Vault
from envault.storage import vault_exists
from envault.env_check import check_vault_against_env


@click.group(name="check")
def check_cli() -> None:
    """Compare vault variables with the current environment."""


@check_cli.command(name="run")
@click.argument("vault_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--extra",
    is_flag=True,
    default=False,
    help="Also report env vars not present in vault.",
)
@click.option(
    "--key",
    "keys",
    multiple=True,
    help="Limit check to specific key(s). Repeatable.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with non-zero status if any issues are found.",
)
def env_check(
    vault_name: str,
    password: str,
    extra: bool,
    keys: tuple,
    strict: bool,
) -> None:
    """Check vault variables against the current shell environment."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)

    try:
        vault = Vault.open(vault_name, password)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Failed to open vault: {exc}", err=True)
        raise SystemExit(1)

    result = check_vault_against_env(
        vault,
        report_extra=extra,
        keys=list(keys) if keys else None,
    )

    if not result.has_issues():
        click.echo("All checks passed. No discrepancies found.")
        return

    for issue in result.issues:
        click.echo(str(issue))

    missing = len(result.by_kind("missing"))
    mismatch = len(result.by_kind("mismatch"))
    extra_count = len(result.by_kind("extra"))
    click.echo(
        f"\nSummary: {missing} missing, {mismatch} mismatched, {extra_count} extra."
    )

    if strict and result.has_issues():
        raise SystemExit(1)
