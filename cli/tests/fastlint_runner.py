##############################################################################
# Prelude
##############################################################################
# Small wrapper around 'fastlint' useful for writing end-to-end (e2e) tests.
#
# old: This file was originally introduced to optimize the way we were running
# fastlint in tests by using Click and its CliRunner to avoid an extra fork.
# However, with the introduction of ofastlint and the new cli/bin/fastlint (which
# dispatch to ofastlint), we actually want to avoid to use the CliRunner which
# only run pyfastlint code. Otherwise, our e2e tests would not be really end-to
# -end and may not represent what the user would get by using fastlint directly.
# This is why using the CliRunner option is now deprecated.
# TODO: The option is still kept because a few of our tests still rely on
# Click-specific features (e.g., mocking)  that the regular
# call-fastlint-in-a-subprocess does not provide yet.
import os
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

from click.testing import CliRunner

##############################################################################
# Constants
##############################################################################

# Environment variable that trigger the use of ofastlint
USE_OFASTLINT = "PYTEST_USE_OFASTLINT" in os.environ

# The --experimental is to force the use of ofastlint.
_OFASTLINT_EXTRA_ARGS = ["--experimental"]

_FASTLINT_PATH = str(
    (
        Path(__file__).parent.parent
        / "src"
        / "fastlint"
        / "console_scripts"
        / "entrypoint.py"
    ).absolute()
)

# Exported constant, convenient to use in a list context.
# This is not safe to use if you are going to append any subcommands after!
# For instance, FASTLINT_BASE_SCAN_COMMAND + ["logout"] will fail with ofastlint,
# because the subcommand must come first.
FASTLINT_BASE_SCAN_COMMAND: List[str] = (
    [_FASTLINT_PATH] + _OFASTLINT_EXTRA_ARGS if USE_OFASTLINT else [_FASTLINT_PATH]
)

FASTLINT_BASE_SCAN_COMMAND_STR: str = " ".join(FASTLINT_BASE_SCAN_COMMAND)

##############################################################################
# Helpers
##############################################################################


def mk_fastlint_base_command(subcommand: str, args: List[str]):
    args = _OFASTLINT_EXTRA_ARGS + args if USE_OFASTLINT else args
    return [_FASTLINT_PATH] + [subcommand] + args


# TODO: this should be removed as we don't want to run tests with Click
@dataclass
class Result:
    """Minimal properties of click.testing.Result used in our project.

    This is for compatibility with the test suite that uses Click
    to run a Python program without launching a new Python interpreter.
    Click is used by the tests to invoke 'fastlint' without incurring
    the 1-second startup delay each time the Python program starts. There's
    no such problem with the OCaml implementation but we must reproduce
    a result object that's sufficiently similar to what the Click invocation
    returns.
    https://click.palletsprojects.com/en/8.0.x/api/#click.testing.Result
    """

    exit_code: int
    stdout: str
    stderr: str

    @property
    def output(self) -> str:
        """alias for stdout"""
        return self.stdout


# Run fastlint in an external process
def fork_fastlint(
    subcommand: Optional[str],
    args: Optional[List[str]],
    env: Optional[Dict[str, str]] = None,
) -> Result:
    argv: List[str] = []

    if args is None:
        args = []

    if subcommand is None:
        argv = FASTLINT_BASE_SCAN_COMMAND + args
    else:
        argv = mk_fastlint_base_command(subcommand, args)

    # ugly: adding --project-root for --help would trigger the wrong help message
    if "-h" in args or "--help" in args:
        argv = [_FASTLINT_PATH] + args

    # env preparation
    env_dict = {}
    if env:
        env_dict = env
    full_env = dict(os.environ, **env_dict)

    # let's fork and use a pipe to communicate with the external fastlint
    print(f"[fork] fastlint command: {' '.join(argv)}", file=sys.stderr)
    proc = Popen(argv, stdout=PIPE, stderr=PIPE, env=full_env)
    stdout, stderr = proc.communicate()
    return Result(proc.returncode, stdout.decode("utf-8"), stderr.decode("utf-8"))


##############################################################################
# Entry point
##############################################################################


class FastlintRunner:
    """Run either fastlint in a subprocess or with CliRunner.

    It's meant as a drop-in replacement for CliRunner(cli, args).
    If a property is missing on the runner object, please add it here.
    """

    def __init__(self, env=None, mix_stderr=True, use_click_runner=False):
        if use_click_runner and USE_OFASTLINT:
            use_click_runner = False
            print("disabling Click_runner use because of PYTEST_USE_OFASTLINT")
        self._use_click_runner = use_click_runner
        self._output = ""
        self._env = env
        self._mix_stderr = mix_stderr
        if self._use_click_runner:
            self._runner = CliRunner(env=env, mix_stderr=mix_stderr)

    def invoke(
        self,
        python_cli,
        args: Union[str, Sequence[str]],
        subcommand: Optional[str] = None,
        input: Optional[str] = None,
        env=None,
    ) -> Result:
        # argv preparation
        arg_list: List[str] = []
        if isinstance(args, str):
            # Parse the list of shell-quoted arguments
            arg_list = shlex.split(args)
        elif isinstance(args, List):
            arg_list = args

        if self._use_click_runner:
            if subcommand:
                arg_list = [subcommand] + arg_list
            print(
                f"[click] fastlint command args: {' '.join(arg_list)}", file=sys.stderr
            )
            result = self._runner.invoke(python_cli, arg_list, input=input, env=env)
            stderr = result.stderr if not self._mix_stderr else ""
            return Result(result.exit_code, result.stdout, stderr)
        else:
            # TODO: do we need to support 'input' i.e. passing a string
            # to the program's stdin?
            if env:
                extra_env = dict(self._env, **env)
            else:
                extra_env = dict(self._env)

            return fork_fastlint(subcommand, arg_list, env=extra_env)
