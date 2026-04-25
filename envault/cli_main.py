"""Main CLI entry point — assembles all sub-command groups."""

import click

from envault.cli import cli as core_cli
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
from envault.cli_backup import backup_cli
from envault.cli_pin import pin_cli
from envault.cli_watch import watch_cli
from envault.cli_promote import promote_cli
from envault.cli_env_diff import env_diff_cli
from envault.cli_env_sync import sync_cli
from envault.cli_validate import validate_cli
from envault.cli_clone import clone_cli
from envault.cli_group import group_cli


def build_cli() -> click.Group:
    """Assemble and return the top-level CLI group."""
    core_cli.add_command(import_cli)
    core_cli.add_command(search_cli)
    core_cli.add_command(copy_cli)
    core_cli.add_command(snapshot_cli)
    core_cli.add_command(tag_cli)
    core_cli.add_command(ttl_cli)
    core_cli.add_command(share_cli)
    core_cli.add_command(lint_cli)
    core_cli.add_command(history_cli)
    core_cli.add_command(profile_cli)
    core_cli.add_command(backup_cli)
    core_cli.add_command(pin_cli)
    core_cli.add_command(watch_cli)
    core_cli.add_command(promote_cli)
    core_cli.add_command(env_diff_cli)
    core_cli.add_command(sync_cli)
    core_cli.add_command(validate_cli)
    core_cli.add_command(clone_cli)
    core_cli.add_command(group_cli)
    return core_cli


main = build_cli()

if __name__ == "__main__":
    main()
