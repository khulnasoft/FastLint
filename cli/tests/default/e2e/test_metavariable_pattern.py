import pytest
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
def test1(run_fastlint_in_tmp: RunFastlint, snapshot):
    # https://github.com/khulnasoft/fastlint/issues/7271
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/metavariable-pattern/test1.json",
            target_name="metavariable-pattern/test1.yml",
            assert_exit_code=2,
        ).stdout,
        "results.json",
    )


@pytest.mark.kinda_slow
def test2(run_fastlint_in_tmp: RunFastlint, snapshot):
    # https://linear.app/r2c/issue/PA-2696
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/metavariable-pattern/test2.yaml",
            target_name="metavariable-pattern/test2.php",
        ).stdout,
        "results.json",
    )
