# Test aliengrep integration in Fastlint rules
import pytest
from tests.fixtures import RunFastlint


@pytest.mark.kinda_slow
@pytest.mark.parametrize(
    "rule,target",
    [
        # Various real-world tests adapted from spacegrep tests.
        ("rules/aliengrep/html.yaml", "aliengrep/html.mustache"),
        ("rules/aliengrep/markdown.yaml", "aliengrep/markdown.md"),
        ("rules/aliengrep/httpresponse.yaml", "aliengrep/httpresponse.txt"),
        ("rules/aliengrep/dockerfile.yaml", "aliengrep/dockerfile"),
        ("rules/aliengrep/multi-lines.yaml", "aliengrep/multi-lines.java"),
        ("rules/aliengrep/terraform.yaml", "aliengrep/terraform.tf"),
        # Aliengrep-specific tests
        ("rules/aliengrep/begin-end.yaml", "aliengrep/begin-end.log"),
        ("rules/aliengrep/long-match.yaml", "aliengrep/long-match.txt"),
        (
            "rules/aliengrep/metavariable-pattern.yaml",
            "aliengrep/metavariable-pattern.conf",
        ),
    ],
)
def test_aliengrep(run_fastlint_in_tmp: RunFastlint, snapshot, rule, target):
    snapshot.assert_match(
        run_fastlint_in_tmp(rule, target_name=target).stdout,
        "results.json",
    )


@pytest.mark.kinda_slow
@pytest.mark.parametrize(
    "rule,target",
    [
        ("rules/aliengrep/nosem-html.yaml", "aliengrep/nosem.html"),
    ],
)
def test_aliengrep_nosem(run_fastlint_in_tmp: RunFastlint, snapshot, rule, target):
    snapshot.assert_match(
        run_fastlint_in_tmp(
            rule, target_name=target, options=["--no-rewrite-rule-ids"]
        ).stdout,
        "results.json",
    )
