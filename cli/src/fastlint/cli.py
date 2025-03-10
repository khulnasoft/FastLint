from typing import Dict

import click

from khulnasoft.commands.ci import ci
from khulnasoft.commands.install import install_fastlint_pro
from khulnasoft.commands.login import login
from khulnasoft.commands.publish import publish
from khulnasoft.commands.scan import scan
from fastlint.default_group import DefaultGroup
from fastlint.git import git_check_output
from fastlint.state import get_state
from fastlint.verbose_logging import getLogger

logger = getLogger(__name__)


def maybe_set_git_safe_directories() -> None:
    """
    Configure Git to be willing to run in any directory when we're in Docker.

    In docker, every path is trusted:
    - the user explicitly mounts their trusted code directory
    - r2c provides every other path

    More info:
    - https://github.blog/2022-04-12-git-security-vulnerability-announced/
    - https://github.com/actions/checkout/issues/766
    """
    env = get_state().env
    if not env.in_docker:
        return

    try:
        # "*" is used over Path.cwd() in case the user targets an absolute path instead of setting --workdir
        git_check_output(["git", "config", "--global", "--add", "safe.directory", "*"])
    except Exception as e:
        logger.info(
            f"Fastlint failed to set the safe.directory Git config option. Git commands might fail: {e}"
        )


@click.group(cls=DefaultGroup, default_command="scan", name="fastlint")
@click.help_option("--help", "-h")
@click.pass_context
def cli(ctx: click.Context) -> None:
    state = get_state()
    state.terminal.init_for_cli()

    commands: Dict[str, click.Command] = ctx.command.commands  # type: ignore
    subcommand: str = (
        ctx.invoked_subcommand if ctx.invoked_subcommand in commands else "unset"
    )

    state.app_session.authenticate()
    state.app_session.user_agent.tags.add(f"command/{subcommand}")
    state.metrics.add_feature("subcommand", subcommand)

    maybe_set_git_safe_directories()


cli.add_command(ci)
cli.add_command(login)
cli.add_command(publish)
cli.add_command(scan)
cli.add_command(install_fastlint_pro)
