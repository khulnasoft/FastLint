import importlib.resources
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

from fastlint.verbose_logging import getLogger

logger = getLogger(__name__)

VERSION_STAMP_FILENAME = "pro-installed-by.txt"

IS_WINDOWS = platform.system() == "Windows"


def compute_executable_path(exec_name: str) -> Optional[str]:
    """
    Determine full executable path if full path is needed to run it.

    Return None if no executable found
    """
    if IS_WINDOWS:
        exec_name += ".exe"

    # First, try packaged binaries
    try:
        with importlib.resources.path("fastlint.bin", exec_name) as path:
            if path.is_file():
                return str(path)
    except FileNotFoundError as e:
        logger.debug(f"Failed to open resource {exec_name}: {e}.")

    # Second, try system binaries in PATH.
    #
    # Environment variables, including PATH, are not inherited by the pytest
    # jobs (at least by default), so this won't work when running pytest
    # tests.
    #
    which_exec = shutil.which(exec_name)
    if which_exec is not None:
        return which_exec

    # Third, look for something in the same dir as the Python interpreter
    relative_path = os.path.join(os.path.dirname(sys.executable), exec_name)
    if os.path.isfile(relative_path):
        return relative_path

    return None


class FastlintCore:
    # Path to the fastlint-core executable, or None if we could not find either
    # or have not looked yet.
    _FASTLINT_PATH_: Optional[str] = None

    _PRO_PATH_: Optional[str] = None

    @classmethod
    def executable_path(cls) -> str:
        """
        Return the path to the fastlint stand-alone executable binary,
        *not* the Python module.  This is intended for unusual cases
        that the module plumbing is not set up to handle.

        Raise Exception if the executable is not found.
        """
        # This method does not bother to cache its result since it is
        # expected to not be a part of any critical path.
        ret = compute_executable_path("fastlint-core")
        if ret is None:
            raise Exception("Could not locate fastlint-core binary")
        return ret

    @classmethod
    def path(cls) -> Path:
        """
        Return the path to the fastlint stand-alone program.  Raise Exception if
        not found.
        """
        if cls._FASTLINT_PATH_ is None:
            cls._FASTLINT_PATH_ = cls.executable_path()

        return Path(cls._FASTLINT_PATH_)

    @classmethod
    def pro_path(cls) -> Optional[Path]:
        if cls._PRO_PATH_ is None:
            cls._PRO_PATH_ = compute_executable_path("fastlint-core-proprietary")

        return Path(cls._PRO_PATH_) if cls._PRO_PATH_ is not None else None

    @classmethod
    def pro_version_stamp_path(cls) -> Path:
        return cls.path().parent / VERSION_STAMP_FILENAME
