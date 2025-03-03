import pytest
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
def test_equivalence(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp("rules/inside.yaml", target_name="basic").stdout,
        "results.json",
    )
