"""CLI commands for linting vault variables."""

from __future__ import annotations

import click

from envault.lint import lint_vault
from envault.vault import Vault
from envault.storage import vault_exists


@click.group(name="lint")
def lint_cli():
    """Lint vault variables for common issues."""


@lint_cli.command(name="check")
@click.argument("vault_name")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False)
@click.option("--errors-only", is_flag=True, default=False, help="Show only errors.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too.")
def lint_check(vault_name: str, password: str, errors_only: bool, strict: bool):
    """Check VAULT_NAME for variable issues."""
    if not vault_exists(vault_name):
        click.echo(f"Error: vault '{vault_name}' does not exist.", err=True)
        raise SystemExit(1)

    try:
        vault = Vault.open(vault_name, password)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    result = lint_vault(vault)

    issues = result.errors() if errors_only else result.issues

    if not issues:
        click.echo(f"✓ No issues found in vault '{vault_name}'.")
        return

    for issue in issues:
        click.echo(str(issue))

    summary_parts = []
    if result.errors():
        summary_parts.append(f"{len(result.errors())} error(s)")
    if not errors_only and result.warnings():
        summary_parts.append(f"{len(result.warnings())} warning(s)")

    click.echo(f"\n{', '.join(summary_parts)} found in vault '{vault_name}'.")

    if result.has_errors or (strict and result.has_warnings):
        raise SystemExit(1)
