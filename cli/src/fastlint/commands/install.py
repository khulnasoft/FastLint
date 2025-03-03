import os
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any
from typing import BinaryIO
from typing import cast

import click
from rich.progress import BarColumn
from rich.progress import DownloadColumn
from rich.progress import Progress
from rich.progress import TextColumn
from rich.progress import TimeRemainingColumn
from rich.progress import TransferSpeedColumn

from fastlint import __VERSION__
from khulnasoft.commands.wrapper import handle_command_errors
from fastlint.console import console
from fastlint.error import FATAL_EXIT_CODE
from fastlint.error import INVALID_API_KEY_EXIT_CODE
from fastlint.fastlint_core import FastlintCore
from fastlint.state import get_state
from fastlint.state import FastlintState
from fastlint.util import abort
from fastlint.util import sub_check_output
from fastlint.verbose_logging import getLogger

logger = getLogger(__name__)


def determine_fastlint_pro_path() -> Path:
    core_path = FastlintCore.path()
    if core_path is None:
        logger.info(
            "Could not find `fastlint-core` executable so not sure where to install fastlint-core-proprietary"
        )
        logger.info("There is something wrong with your fastlint installation")
        sys.exit(FATAL_EXIT_CODE)

    fastlint_pro_path = Path(core_path).parent / "fastlint-core-proprietary"
    return fastlint_pro_path


# This places a stamp alongside the fastlint-core-proprietary binary indicating
# which version of Fastlint installed it. This allows us to ensure that we are
# not running an out-of-date binary if Fastlint is later upgraded but the
# fastlint-core-proprietary binary remains in place.
#
# See also engine.py check_is_correct_pro_version
def add_fastlint_pro_version_stamp() -> None:
    path = FastlintCore.pro_version_stamp_path()
    with path.open("w") as f:
        f.write(__VERSION__)


def download_fastlint_pro(
    state: FastlintState, platform_kind: str, destination: Path
) -> None:
    url = f"{state.env.fastlint_url}/api/agent/deployments/deepbinary/{platform_kind}?version={__VERSION__}"
    logger.debug(f"downloading from {url}")

    with state.app_session.get(url, timeout=180, stream=True) as r:
        if r.status_code == 401:
            logger.info(
                "API token not valid. Try to run `fastlint logout` and `fastlint login` again. "
                "Or in CI, ensure your FASTLINT_APP_TOKEN variable is set correctly."
            )
            sys.exit(INVALID_API_KEY_EXIT_CODE)
        if r.status_code == 403:
            logger.warning(
                "Logged in deployment does not have access to Fastlint Pro Engine"
            )
            # FIXME: Needs to be updated before launch Feb 2023
            logger.warning(
                "Visit https://fastlint.dev/products/pro-engine/ for more information."
            )
            sys.exit(FATAL_EXIT_CODE)
        r.raise_for_status()

        # Make sure no such binary exists. We have had weird situations when the
        # downloaded binary was corrupted, and overwriting it did not fix it, but
        # it was necessary to `rm -f` it.
        if destination.exists():
            destination.unlink()

        file_size = int(r.headers.get("Content-Length", 0))

        # I (nmote) think the typings for this are wrong. This works at runtime,
        # and when adding the necessary `instanceof` checks to satisfy mypy, I
        # actually got a runtime failure. Looks like some discrepancy between
        # http.client.HTTPResponse and urllib3.response.HTTPResponse. Maybe the
        # typings picked the wrong one?
        raw_response: BinaryIO = cast(Any, r.raw)
        with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress, destination.open("wb") as f, progress.wrap_file(
            raw_response, total=file_size, description="Downloading..."
        ) as r_raw:
            shutil.copyfileobj(r_raw, f)


def run_install_fastlint_pro() -> None:
    fastlint_pro_path = determine_fastlint_pro_path()

    # TODO This is a temporary solution to help offline users
    logger.info(f"Fastlint Pro Engine will be installed in {fastlint_pro_path}")

    if fastlint_pro_path.exists():
        logger.info(f"Overwriting Fastlint Pro Engine already installed!")

    state = get_state()
    if state.app_session.token is None:
        logger.info(
            "Run `fastlint login` before running `fastlint install-fastlint-pro`. "
            "Or in non-interactive environments, ensure your FASTLINT_APP_TOKEN variable is set correctly."
        )
        sys.exit(INVALID_API_KEY_EXIT_CODE)

    logger.debug(f"platform is {sys.platform}")
    # TODO: cleanup and use consistent arch name like in pro-release.jsonnet
    if sys.platform.startswith("darwin"):
        # TODO? other arms than arm64? let's just check a prefix.
        if platform.machine().startswith("arm"):
            platform_kind = "osx-arm64"
        else:
            platform_kind = "osx-x86_64"
    elif sys.platform.startswith("linux"):
        if platform.machine().startswith("arm") or platform.machine().startswith(
            "aarch"
        ):
            platform_kind = "linux-arm64"
        else:
            platform_kind = "manylinux"
    else:
        platform_kind = "manylinux"
        logger.info(
            "Running on potentially unsupported platform. Installing linux compatible binary"
        )

    # Download the binary into a temporary location, check it, then install it.
    # This should prevent bad installations.

    fastlint_pro_path_tmp = fastlint_pro_path.with_suffix(".tmp_download")

    download_fastlint_pro(state, platform_kind, fastlint_pro_path_tmp)

    # THINK: Do we need to give exec permissions to everybody? Can this be a security risk?
    #        The binary should not have setuid or setgid rights, so letting others
    #        execute it should not be a problem.
    # nofastlint: tests.precommit_dogfooding.python.lang.security.audit.insecure-file-permissions.insecure-file-permissions
    os.chmod(
        fastlint_pro_path_tmp,
        os.stat(fastlint_pro_path_tmp).st_mode
        | stat.S_IEXEC
        | stat.S_IXGRP
        | stat.S_IXOTH,
    )

    # Get Pro version, it serves as a simple check that the binary works
    try:
        version = sub_check_output(
            [str(fastlint_pro_path_tmp), "-pro_version"],
            timeout=10,
            encoding="utf-8",
            stderr=subprocess.STDOUT,
        ).rstrip()
    except subprocess.CalledProcessError:
        if fastlint_pro_path_tmp.exists():
            fastlint_pro_path_tmp.unlink()
        abort(
            "Downloaded binary failed version check, try again or contact support@khulnasoft.com"
        )

    # Version check worked so we now install the binary
    if fastlint_pro_path.exists():
        fastlint_pro_path.unlink()
    fastlint_pro_path_tmp.rename(fastlint_pro_path)
    add_fastlint_pro_version_stamp()
    logger.info(f"\nSuccessfully installed Fastlint Pro Engine (version {version})!")


@click.command()
@click.option(
    "--debug",
    is_flag=True,
)
@handle_command_errors
def install_fastlint_pro(debug: bool) -> None:
    state = get_state()
    state.terminal.configure(verbose=False, debug=debug, quiet=False, force_color=False)

    run_install_fastlint_pro()
