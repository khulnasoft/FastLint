import pytest
from tests.fixtures import RunFastlint

from fastlint.constants import OutputFormat

# was in e2e/test_output.py before


@pytest.mark.kinda_slow
@pytest.mark.osemfail
def test_cli_test_secret_rule(run_fastlint_in_tmp: RunFastlint, snapshot):
    results, _ = run_fastlint_in_tmp(
        "rules/secrets.yaml",
        target_name="basic.py",
        output_format=OutputFormat.TEXT,
        force_color=True,
    )
    snapshot.assert_match(
        results,
        "results.txt",
    )
