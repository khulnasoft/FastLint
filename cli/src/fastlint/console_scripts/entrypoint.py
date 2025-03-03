#!/usr/bin/env python3
# This file is the Fastlint CLI entry point of the Fastlint pip package,
# the Fastlint HomeBrew package, and the Fastlint Docker container.
#
# In the future we may have different entry points when packaging Fastlint
# with Cargo, Npm, Opam, or even with Docker (ideally the entry point would
# be src/main/Main.ml without any wrapper around once ofastlint is finished).
#
# The main purpose of this small wrapper is to dispatch
# either to the legacy pyfastlint (see the pyfastlint script in this
# directory), or to the new ofastlint (accessible via the fastlint-core binary
# under cli/src/fastlint/bin/ or somewhere in the PATH), or even to
# ofastlint-pro (accessible via the fastlint-core-proprietary binary).
#
# It would be faster and cleaner to have a Bash script instead of a Python
# script here, but actually the overhead of Python here is just 0.015s.
# Moreover, it is sometimes hard from a Bash script to find where is installed
# fastlint-core, but it is simple from Python because you can simply use
# importlib.resources. We could also use 'pip show fastlint' from a Bash script
# to find fastlint-core, but will 'pip' be in the PATH? Should we use 'pip' or
# 'pip3'?
# Again, it is simpler to use a Python script and leverage importlib.resources.
# Another alternative would be to always have fastlint-core in the PATH,
# but when trying to put this binary in cli/bin, setuptools is yelling
# and does not know what to do with it. In the end, it is simpler to use
# a *Python* script when installed via a *Python* package manager (pip).
#
# NOTE: if you modify this file, you will need to `pipenv install --dev`
# if you want to test the change under `pipenv shell`.
import importlib.resources
import os
import platform
import shutil
import sys
import sysconfig
import warnings

# alt: you can also add '-W ignore::DeprecationWarning' after the python3 above,
# but setuptools and pip adjust this line when installing fastlint so we need
# to do this instead.

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add the directory containing this script in the PATH, so the pyfastlint
# script will also be in the PATH.
# Some people don't have fastlint in their PATH and call it instead
# explicitly as in /path/to/somewhere/bin/fastlint, but this means
# that calling pyfastlint from ofastlint would be difficult because
# it would not be in the PATH (we would need to pass its path to ofastlint,
# which seems more complicated).
# nosem: no-env-vars-on-top-level
PATH = os.environ.get("PATH", "")
# nosem: no-env-vars-on-top-level
os.environ["PATH"] = PATH + os.pathsep + sysconfig.get_path("scripts")

IS_WINDOWS = platform.system() == "Windows"

PRO_FLAGS = ["--pro", "--pro-languages", "--pro-intrafile"]


class CoreNotFound(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


# Similar to cli/src/fastlint/engine.py check_is_correct_pro_version
def is_correct_pro_version(core_path):
    """
    We want to be careful about what we import here in order to keep this
    script lightweight. However, this file just defines a single constant and
    it takes well under a millisecond to import this.

    This can be verified with `time python -c 'import fastlint; print(fastlint.__VERSION__)'`
    """
    from fastlint import __VERSION__

    # Duplicate of cli/src/fastlint/fastlint_core.py pro_version_stamp_path
    stamp_path = core_path.parent / "pro-installed-by.txt"
    if stamp_path.is_file():
        with stamp_path.open("r") as f:
            version_at_install = f.readline().strip()
            return version_at_install == __VERSION__
    else:
        return False


# similar to cli/src/fastlint/fastlint_core.py compute_executable_path()
def find_fastlint_core_path(pro=False, extra_message=""):
    if pro:
        core = "fastlint-core-proprietary"
    else:
        core = "fastlint-core"

    if IS_WINDOWS:
        core += ".exe"

    # First, try the packaged binary.
    try:
        # the use of .path causes a DeprecationWarning hence the
        # filterwarnings above
        with importlib.resources.path("fastlint.bin", core) as path:
            if path.is_file():
                if pro and not is_correct_pro_version(path):
                    raise CoreNotFound(
                        f"The installed version of {core} is out of date.{extra_message}"
                    )
                return str(path)
    except (FileNotFoundError, ModuleNotFoundError):
        pass

    # Second, try in PATH. In certain context such as Homebrew
    # (see https://github.com/Homebrew/homebrew-core/blob/master/Formula/fastlint.rb)
    # or Docker (see ../../Dockerfile), we actually copy fastlint-core in
    # /usr/local/bin (or in a bin/ folder in the PATH). In those cases,
    # there is no /.../site-packages/fastlint-xxx/bin/fastlint-core.
    # In those cases, we want to grab fastlint-core from the PATH instead.
    path = shutil.which(core)
    if path is not None:
        return path

    raise CoreNotFound(
        f"Failed to find {core} in PATH or in the fastlint package.{extra_message}"
    )


# TODO: we should just do 'execvp("pyfastlint", sys.argv)'
# but this causes some regressions with --test (see PA-2963)
# and autocomplete (see #8359)
# TODO: we should get rid of autocomplete anyway (it's a Python Click
# thing not supported by ofastlint anyway),
# TODO: we should fix --test instead.
# The past investigation of Austin is available in #8360 PR comments
def exec_pyfastlint():
    import fastlint.main

    sys.exit(fastlint.main.main())


# We could have moved the code below in a separate 'ofastlint' file, like
# for 'pyfastlint', but we don't want users to be exposed to another command,
# so it is better to hide it.
# We expose 'pyfastlint' because ofastlint itself might need to fallback to
# pyfastlint and it's better to avoid the possibility of an infinite loop
# by simply using a different program name. Morever, in case of big problems,
# we can always tell users to run pyfastlint instead of fastlint and be sure
# they'll get the old behavior.
def exec_ofastlint():
    argv = sys.argv
    if any(pro_flag in argv for pro_flag in PRO_FLAGS):
        try:
            path = find_fastlint_core_path(
                pro=True,
                extra_message="\nYou may need to run `fastlint install-fastlint-pro`",
            )
        except CoreNotFound as e:
            print(str(e), file=sys.stderr)
            if sys.argv[1] == "ci":
                # CI users usually want things to just work. In particular, if they
                # are running `fastlint ci --pro` they don't want to have to add an
                # extra step to install-fastlint-pro. This wrapper doesn't have a way
                # to install fastlint-pro, however, so have them run legacy `fastlint`.
                print(
                    "Since `fastlint ci` was run, defaulting to legacy fastlint",
                    file=sys.stderr,
                )
                exec_pyfastlint()
            else:
                sys.exit(2)
        # If you call fastlint-core-proprietary as ofastlint-pro, then we get
        # ofastlint-pro behavior, see fastlint-proprietary/src/main/Pro_main.ml
        sys.argv[0] = "ofastlint-pro"
    else:
        try:
            path = find_fastlint_core_path()
        except CoreNotFound as e:
            print(str(e), file=sys.stderr)
            # fatal error, see src/ofastlint/core/Exit_code.ml
            sys.exit(2)

        # If you call fastlint-core as ofastlint, then we get
        # ofastlint behavior, see src/main/Main.ml
        sys.argv[0] = "ofastlint"
    # nosem: dangerous-os-exec-tainted-env-args
    os.execvp(str(path), sys.argv)


# Needed for similar reasons as in pyfastlint, but only for the legacy
# flag to work
def main():
    # escape hatch for users to pyfastlint in case of problems (they
    # can also call directly 'pyfastlint').
    if "--legacy" in sys.argv:
        sys.argv.remove("--legacy")
        exec_pyfastlint()
    elif "--experimental" in sys.argv:
        exec_ofastlint()
    else:
        # we now default to ofastlint! but this will usually exec
        # back to pyfastlint for most commands (for now)
        # We activate the new CLI UX only when fastlint is invoked directly
        # (and legacy is not specified)
        # and ofastlint needs to fallback on pyfastlint
        os.environ["FASTLINT_NEW_CLI_UX"] = f"{int(sys.stdout.isatty())}"
        exec_ofastlint()


if __name__ == "__main__":
    main()
