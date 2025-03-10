import pytest
from tests.fixtures import RunFastlint


# ofastlint returns the target correctly as not scanned but pyfastlint
# marks it as scanned.
# TODO: exclude pysemfail tests or fix the problem in pyfastlint (output.py)
# See comment in Scan_subcommand.ml.
# @pytest.mark.pysemfail
@pytest.mark.kinda_slow
@pytest.mark.osemfail
def test_pro_rule_skipping(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/pro-rule-skipping.yaml", target_name="pro-rule-skipping/x.cls"
        ).stdout,
        "results.json",
    )


# see comment above regarding pysemfail
# @pytest.mark.pysemfail
@pytest.mark.kinda_slow
@pytest.mark.osemfail
def test_pro_rule_skipping_no_parsing(run_fastlint_in_tmp: RunFastlint, snapshot):
    snapshot.assert_match(
        run_fastlint_in_tmp(
            "rules/pro-rule-skipping-no-parsing.yaml",
            target_name="pro-rule-skipping-no-parsing/x.cls",
        ).stdout,
        "results.json",
    )
