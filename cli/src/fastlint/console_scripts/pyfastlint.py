#!/usr/bin/env python3
# This script will be installed by pip somewhere in PATH (e.g., /opt/local/bin/)
# because it's mentioned in ../setup.py with 'scripts=[..., "bin/pyfastlint"]'.
# Thus, ofastlint can easily fallback to pyfastlint (without any further
# dispatch like in fastlint) by simply calling 'execvp("pyfastlint", ...)'.
#
# Note that the first bang line above is adjusted by 'pipenv install' or 'pip'
# to point to the "right" Python interpreter (e.g., /opt/local/bin/python3.11),
# the one linked to the 'pip' used to install fastlint. This Python interpreter
# then knows where to find the Fastlint Python source files referenced below
# with fastlint.main.main
# (e.g., in /opt/local/lib/site-packages/python3.11/fastlint/)
import os
import sys

# This file is not part of the Python 'fastlint' package; it's a script.
# It's an escape hatch for users to pyfastlint in case of problems.


# Python module system and multiprocessing weirdness below
# --------------------------------------------------------
# When python imports a module, i.e. `import fastlint.FOO`, it runs the module's
# top-level code, which is the code that is not inside any function or class.
# This means that if we try and run a function from the fastlint package in a
# subprocess, we would end up calling os.execvp() above or main() below, which
# cause a bunch of errors. So we need to make sure that we only run the code
# below when this file is run as an executable, hence the guard below.
# This fix a crash when using fastlint --test (which apparently triggers
# execution of this file).
# Austin: the above explanation is my understanding, but I think Python
# is weirder under the hood with this stuff.
# Pad: I don't understand why the use of '--test' triggers the code here;
# if '--test' use fastlint.Foo, it should execute code in cli/src/fastlint/__init__.php
# Austin: I don't understand either. What's even weirder is this script also needs it
# even though it's not the same mainspace as the fastlint package. After encountering
# this error again my best guess is that python multiprocessing actually clones the
# OS process, instead of just starting a new python process and importing the fastlint
# module before running the function given to multiprocessing. I.e. you would expect
# multiprocessing under the hood to do something like
# python3 -m fastlint.MULTI_PROCESS_FUNCTION
# for each process, but instead it most likely does something like
# os.execvp(sys.argv[0], sys.argv + [MULTI_PROCESS_FUNCTION])
#
# See safe importing of main modules here:
# https://docs.python.org/3/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
# It doesn't explain in enough detail to give a real answer, hence the guess above.
def main():
    # Only enable new CLI UX when pyfastlint is invoked directly and with interactive terminal
    os.environ["FASTLINT_NEW_CLI_UX"] = f"{int(sys.stdout.isatty())}"
    import fastlint.main

    sys.exit(fastlint.main.main())


if __name__ == "__main__":
    main()
