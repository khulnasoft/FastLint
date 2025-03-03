import shutil
from pathlib import Path

import pytest
from tests.conftest import mask_variable_text
from tests.conftest import TARGETS_PATH
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
def test_fastlintignore(run_fastlint_in_tmp: RunFastlint, tmp_path, snapshot):
    (tmp_path / ".fastlintignore").symlink_to(
        Path(TARGETS_PATH / "ignores" / ".fastlintignore").resolve()
    )
    # BUG: pyfastlint doesn't complain if an included file is missing
    # This file is included by the .fastlintignore above.
    # It must be a regular file, not a symlink (enforced in ofastlint).
    shutil.copyfile(
        Path(TARGETS_PATH / "ignores" / ".gitignore"), tmp_path / ".gitignore"
    )

    snapshot.assert_match(
        run_fastlint_in_tmp("rules/eqeq-basic.yaml", target_name="ignores").stdout,
        "results.json",
    )


# We provide no .fastlintignore but everything except find.js should still
# be ignored
@pytest.mark.kinda_slow
def test_default_fastlintignore(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/eqeq-basic.yaml", target_name="ignores_default"
        ).stdout,
        "results.json",
    )


# Input from stdin will not have a path that is relative to tmp_path, where we're running fastlint
@pytest.mark.kinda_slow
@pytest.mark.osemfail
def test_file_not_relative_to_base_path(run_fastlint: RunFastlint, snapshot):
    results = run_fastlint(
        options=["--json", "-e", "a", "--lang", "js", "-"],
        stdin="a",
        use_click_runner=True,  # TODO: probably because of stdin?
    )
    results.raw_stdout = mask_variable_text(results.raw_stdout)
    snapshot.assert_match(results.as_snapshot(), "results.txt")


# Test the specification of a fastlintignore file via the environment
# variable FASTLINT_R2C_INTERNAL_EXPLICIT_FASTLINTIGNORE.
# This is for fastlint-action. See run_scan.py.
@pytest.mark.kinda_slow
@pytest.mark.osemfail
def test_internal_explicit_fastlintignore(
    run_fastlint_in_tmp: RunFastlint, tmp_path, snapshot
):
    (tmp_path / ".fastlintignore").symlink_to(
        Path(TARGETS_PATH / "ignores" / ".fastlintignore").resolve()
    )

    explicit_ignore_file = tmp_path / ".fastlintignore_explicit"
    explicit_ignore_file.touch()

    env = {"FASTLINT_R2C_INTERNAL_EXPLICIT_FASTLINTIGNORE": str(explicit_ignore_file)}
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/eqeq-basic.yaml", target_name="ignores", env=env
        ).stdout,
        "results.json",
    )
