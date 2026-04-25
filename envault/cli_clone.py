"""CLI commands for cloning vaults."""

from __future__ import annotations

import click

from envault.env_clone import clone_vault, CloneError


@click.group(name="clone")
def clone_cli() -> None:
    """Clone variables between vaults."""


@clone_cli.command(name="run")
@click.argument("source")
@click.argument("destination")
@click.option("--source-password", prompt=True, hide_input=True, help="Source vault password.")
@click.option("--dest-password", prompt=True, hide_input=True, confirmation_prompt=True, help="Destination vault password.")
@click.option("--pattern", default=None, help="Glob pattern to filter keys (e.g. 'DB_*').")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
def clone_run(
    source: str,
    destination: str,
    source_password: str,
    dest_password: str,
    pattern: str | None,
    overwrite: bool,
) -> None:
    """Clone variables from SOURCE vault into DESTINATION vault."""
    try:
        result = clone_vault(
            source_name=source,
            source_password=source_password,
            dest_name=destination,
            dest_password=dest_password,
            pattern=pattern,
            overwrite=overwrite,
        )
    except CloneError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(result.summary())
    if result.copied:
        click.echo("Copied keys:")
        for key in sorted(result.copied):
            click.echo(f"  {key}")
    if result.skipped:
        click.echo("Skipped keys:")
        for key in sorted(result.skipped):
            click.echo(f"  {key}")
