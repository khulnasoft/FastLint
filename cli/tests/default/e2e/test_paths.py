import pytest
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
def test_paths(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp("rules/paths.yaml", target_name="exclude_include").stdout,
        "results.json",
    )
