import pytest
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
def test_version_constraints(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/version-constraints.yaml", target_name="version-constraints/x.py"
        ).stdout,
        "results.json",
    )
