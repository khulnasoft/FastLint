# TODO: This file should be deleted! The only stable API is to
# use the fastlint CLI with --json and follow fastlint_output_v1.atd.
# External users should not rely on any Python API as pyfastlint
# will soon be gone.
import os
import subprocess
import sys
from pathlib import Path

import pytest
from tests.fixtures import RunFastlint

from fastlint.run_scan import run_scan_and_return_json


# When calling ofastlint, stderr isn't available via this 'capsys' object,
# causing the test to pass when it shouldn't.
# TODO: use FastlintRunner instead, which is drop-in replacement for CliRunner.
@pytest.mark.slow
@pytest.mark.todo
@pytest.mark.osemfail
def test_api(unique_home_dir, capsys, run_fastlint_in_tmp: RunFastlint):
    # Test that exposed python API works and prints out nothing to stderr or stdout
    # unique_home_dir is used to ensure that the test runs with it's own
    # settings.yaml file to avoid reading one corrupted by another concurrent test run.
    output = run_scan_and_return_json(
        config=Path("rules/eqeq.yaml"),
        scanning_roots=[
            Path("targets/bad/invalid_python.py"),
            Path("targets/basic/stupid.py"),
        ],
    )

    captured = capsys.readouterr()
    assert isinstance(output, dict)
    assert len(output["errors"]) == 1
    assert len(output["results"]) == 1
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.slow
@pytest.mark.no_fastlint_cli
def test_api_via_cli(unique_home_dir, run_fastlint_in_tmp: RunFastlint):
    # Check that logging code isnt handled by default root handler and printed to stderr
    # This is run as a separate test from the one above so that it has a separate, temp directory
    env = os.environ.copy()
    # Assign env var for settings.yaml to the per-test unique home directory
    # so it doesn't use the default (~/.fastlint/settings.yaml)
    env["FASTLINT_SETTINGS_FILE"] = str(unique_home_dir / ".fastlint/settings.yaml")
    x = subprocess.run(
        [
            sys.executable,
            "-c",
            "from fastlint.run_scan import run_scan_and_return_json; from pathlib import Path; run_scan_and_return_json(config=Path('rules/eqeq.yaml'),scanning_roots=[Path('targets/bad/invalid_python.py'), Path('targets/basic/stupid.py')],)",
        ],
        encoding="utf-8",
        capture_output=True,
        env=env,
    )
    assert x.stdout == ""
    assert x.stderr == ""
