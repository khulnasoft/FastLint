import pytest
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
def test_severity_error(run_fastlint_in_tmp: RunFastlint, snapshot):
    json_str = run_fastlint_in_tmp(
        "rules/inside.yaml", options=["--severity", "ERROR"]
    ).stdout
    assert json_str != ""
    assert '"severity": "INFO"' not in json_str
    assert '"severity": "WARNING"' not in json_str
    snapshot.assert_match(json_str, "results.json")


@pytest.mark.kinda_slow
def test_severity_info(run_fastlint_in_tmp: RunFastlint, snapshot):
    # Shouldn't return errors or results, since inside.yaml has 'severity: ERROR'
    snapshot.assert_match(
        run_fastlint_in_tmp("rules/inside.yaml", options=["--severity", "INFO"]).stdout,
        "results.json",
    )


@pytest.mark.kinda_slow
def test_severity_warning(run_fastlint_in_tmp: RunFastlint, snapshot):
    # Shouldn't return errors or results, since inside.yaml has 'severity: ERROR'
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/inside.yaml", options=["--severity", "WARNING"]
        ).stdout,
        "results.json",
    )


@pytest.mark.kinda_slow
def test_severity_multiple(run_fastlint_in_tmp: RunFastlint, snapshot):
    # Shouldn't return errors or results, since inside.yaml has 'severity: ERROR'
    # Differs from the two preceding tests in that we're testing adding multiple severity strings
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/inside.yaml", options=["--severity", "INFO", "--severity", "WARNING"]
        ).stdout,
        "results.json",
    )
