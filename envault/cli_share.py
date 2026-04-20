"""CLI commands for sharing vault variables via signed bundles."""

import click
from envault.vault import Vault
from envault.share import create_bundle, open_bundle, ShareError, DEFAULT_TTL_SECONDS


@click.group(name="share")
def share_cli():
    """Share variables via signed, time-limited bundles."""


@share_cli.command("create")
@click.argument("vault_name")
@click.argument("password")
@click.argument("secret")
@click.option("--keys", "-k", multiple=True, help="Keys to include (default: all).")
@click.option("--ttl", default=DEFAULT_TTL_SECONDS, show_default=True, help="Bundle TTL in seconds.")
@click.option("--label", default=None, help="Optional label for the bundle.")
def share_create(vault_name, password, secret, keys, ttl, label):
    """Create a signed share bundle from VAULT_NAME."""
    v = Vault(vault_name)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        v.open(password)
    except Exception:
        click.echo("Failed to open vault. Wrong password?", err=True)
        raise SystemExit(1)

    all_keys = v.keys()
    selected = list(keys) if keys else all_keys
    missing = [k for k in selected if k not in all_keys]
    if missing:
        click.echo(f"Keys not found in vault: {', '.join(missing)}", err=True)
        raise SystemExit(1)

    variables = {k: v.get(k) for k in selected}
    try:
        bundle = create_bundle(variables, secret, ttl=ttl, label=label)
    except ShareError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(bundle)


@share_cli.command("import")
@click.argument("vault_name")
@click.argument("password")
@click.argument("secret")
@click.argument("bundle")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def share_import(vault_name, password, secret, bundle, overwrite):
    """Import variables from a signed BUNDLE into VAULT_NAME."""
    v = Vault(vault_name)
    if not v.exists():
        click.echo(f"Vault '{vault_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        v.open(password)
    except Exception:
        click.echo("Failed to open vault. Wrong password?", err=True)
        raise SystemExit(1)

    try:
        variables = open_bundle(bundle, secret)
    except ShareError as exc:
        click.echo(f"Bundle error: {exc}", err=True)
        raise SystemExit(1)

    imported = []
    skipped = []
    for key, value in variables.items():
        if key in v.keys() and not overwrite:
            skipped.append(key)
            continue
        v.set(key, value)
        imported.append(key)

    v.save()
    if imported:
        click.echo(f"Imported: {', '.join(imported)}")
    if skipped:
        click.echo(f"Skipped (already exist): {', '.join(skipped)}")
