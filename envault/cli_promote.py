"""CLI commands for promoting variables between vaults."""

from __future__ import annotations

import click

from envault.vault import Vault
from envault.storage import vault_exists
from envault.env_promote import promote_variables, PromoteError


@click.group(name="promote")
def promote_cli() -> None:
    """Promote variables from one vault to another."""


@promote_cli.command(name="run")
@click.argument("src")
@click.argument("dst")
@click.option("--password", prompt=True, hide_input=True, help="Shared vault password.")
@click.option(
    "--key",
    "keys",
    multiple=True,
    metavar="KEY",
    help="Key(s) to promote (repeatable).  Omit to promote all.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys in the destination vault.",
)
def promote_run(
    src: str,
    dst: str,
    password: str,
    keys: tuple[str, ...],
    overwrite: bool,
) -> None:
    """Promote variables from SRC vault to DST vault."""
    if not vault_exists(src):
        click.echo(f"Error: source vault '{src}' does not exist.", err=True)
        raise SystemExit(1)
    if not vault_exists(dst):
        click.echo(f"Error: destination vault '{dst}' does not exist.", err=True)
        raise SystemExit(1)

    try:
        src_vault = Vault.open(src, password)
        dst_vault = Vault.open(dst, password)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error opening vault: {exc}", err=True)
        raise SystemExit(1)

    selected_keys: list[str] | None = list(keys) if keys else None

    try:
        result = promote_variables(src_vault, dst_vault, keys=selected_keys, overwrite=overwrite)
    except PromoteError as exc:
        click.echo(f"Promote error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(result.summary())
