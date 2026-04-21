"""Main CLI entry point that registers all sub-command groups including profile."""

import click
from envault.cli import cli
from envault.cli_import import import_cli
from envault.cli_search import search_cli
from envault.cli_copy import copy_cli
from envault.cli_snapshot import snapshot_cli
from envault.cli_tags import tag_cli
from envault.cli_ttl import ttl_cli
from envault.cli_share import share_cli
from envault.cli_lint import lint_cli
from envault.cli_history import history_cli
from envault.cli_profile import profile_cli


def build_cli() -> click.Group:
    """Attach all sub-groups to the root CLI and return it."""
    cli.add_command(import_cli)
    cli.add_command(search_cli)
    cli.add_command(copy_cli)
    cli.add_command(snapshot_cli)
    cli.add_command(tag_cli)
    cli.add_command(ttl_cli)
    cli.add_command(share_cli)
    cli.add_command(lint_cli)
    cli.add_command(history_cli)
    cli.add_command(profile_cli)
    return cli


main = build_cli()

if __name__ == "__main__":
    main()
