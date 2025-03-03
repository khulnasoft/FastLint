import pytest
from tests.conftest import _clean_stdout
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
def test_regex_rule__nofastlint(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/regex/regex-nofastlint.yaml", target_name="basic/regex-nofastlint.txt"
        ).stdout,
        "results.json",
    )


@pytest.mark.kinda_slow
def test_nosem_rule(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(run_fastlint_in_tmp("rules/nosem.yaml").stdout, "results.json")


@pytest.mark.kinda_slow
@pytest.mark.osemfail
def test_nosem_rule__invalid_id(run_fastlint_in_tmp: RunFastlint, snapshot):
    stdout, stderr = run_fastlint_in_tmp(
        "rules/nosem.yaml", target_name="nosem_invalid_id", assert_exit_code=2
    )

    snapshot.assert_match(stderr, "error.txt")
    snapshot.assert_match(_clean_stdout(stdout), "error.json")


@pytest.mark.kinda_slow
def test_nosem_with_multiple_ids(run_fastlint_in_tmp: RunFastlint):
    run_fastlint_in_tmp(
        "rules/two_matches.yaml",
        target_name="nofastlint/multiple-nofastlint.py",
        assert_exit_code=0,
    )


@pytest.mark.kinda_slow
def test_nosem_rule__with_disable_nosem(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp("rules/nosem.yaml", options=["--disable-nosem"]).stdout,
        "results.json",
    )
