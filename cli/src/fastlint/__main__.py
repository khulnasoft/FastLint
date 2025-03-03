#!/usr/bin/env python3
import sys

if __name__ == "__main__":
    sys.stderr.write(
        "Using `python -m fastlint` to run Fastlint is deprecated as of 1.38.0. Please simply run `fastlint` instead.\n"
    )
    sys.exit(2)
