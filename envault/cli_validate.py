"""CLI commands for validating vault variables against a schema."""

import json
import sys

import click

from envault.storage import vault_exists
from envault.vault import Vault
from envault.env_validate import validate_vault


@click.group(name="validate")
def validate_cli():
    """Validate vault variables against required keys and patterns."""


@validate_cli.command(name="check")
@click.argument("vault_name")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
@click.option("--require", "required_keys", multiple=True, metavar="KEY",
              help="Keys that must be present in the vault.")
@click.option("--pattern", "raw_patterns", multiple=True, metavar="KEY=REGEX",
              help="Key=pattern pairs; value must match the regex.")
@click.option("--schema", "schema_file", default=None, type=click.Path(exists=True),
              help="JSON schema file with 'required' and 'patterns' fields.")
@click.option("--allow-empty", is_flag=True, default=False,
              help="Suppress warnings for empty values.")
def validate_check(vault_name, password, required_keys, raw_patterns, schema_file, allow_empty):
    """Check vault variables against required keys and value patterns."""
    if not vault_exists(vault_name):
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        sys.exit(1)

    try:
        vault = Vault.open(vault_name, password)
    except Exception as exc:
        click.echo(f"Failed to open vault: {exc}", err=True)
        sys.exit(1)

    required = list(required_keys)
    patterns = {}

    for entry in raw_patterns:
        if "=" not in entry:
            click.echo(f"Invalid pattern spec '{entry}', expected KEY=REGEX.", err=True)
            sys.exit(1)
        k, v = entry.split("=", 1)
        patterns[k] = v

    if schema_file:
        with open(schema_file) as fh:
            schema = json.load(fh)
        required += schema.get("required", [])
        patterns.update(schema.get("patterns", {}))

    result = validate_vault(vault, required_keys=required, patterns=patterns, allow_empty=allow_empty)

    if not result.issues:
        click.echo("All checks passed.")
        return

    for issue in result.issues:
        click.echo(str(issue))

    if result.has_errors():
        sys.exit(2)
