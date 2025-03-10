import pytest
from tests.fixtures import RunFastlint

from fastlint.constants import OutputFormat


@pytest.mark.kinda_slow
@pytest.mark.parametrize(
    "rule",
    [
        ("rules/invalid-rules/invalid-metavariable-regex.yaml"),
        ("rules/invalid-rules/invalid-pattern-child.yaml"),
        ("rules/invalid-rules/invalid-missing-top-item.yaml"),
        ("rules/invalid-rules/invalid-pattern.yaml"),
        ("rules/invalid-rules/invalid-pattern-operator.yaml"),
        ("rules/invalid-rules/additional-invalid-pattern-operator.yaml"),
        ("rules/invalid-rules/string-pattern.yaml"),
        ("rules/invalid-rules/string-pattern-under-patterns.yaml"),
        ("rules/invalid-rules/missing-hyphen.yaml"),
        ("rules/invalid-rules/missing-pattern.yaml"),
    ],
)
@pytest.mark.osemfail
def test_validation_of_invalid_rules(run_fastlint_in_tmp: RunFastlint, snapshot, rule):
    _, err = run_fastlint_in_tmp(
        rule,
        options=["--validate"],
        output_format=OutputFormat.TEXT,
        assert_exit_code={2, 4},
    )

    snapshot.assert_match(
        err,
        "results.txt",
    )


@pytest.mark.kinda_slow
@pytest.mark.parametrize(
    "rule",
    [
        ("rules/extra_field.yaml"),
    ],
)
@pytest.mark.osemfail
def test_extra_top_level_valid(run_fastlint_in_tmp: RunFastlint, snapshot, rule):
    """
    An extra field in the rule does not cause it to fail validation
    """
    _, err = run_fastlint_in_tmp(
        rule,
        options=["--validate"],
        output_format=OutputFormat.TEXT,
        assert_exit_code={0},
    )

    snapshot.assert_match(
        err,
        "results.txt",
    )


@pytest.mark.kinda_slow
@pytest.mark.parametrize(
    "rule",
    [
        "rules/regex/regex-capture-groups.yaml",
        "rules/regex/numeric-regex-capture-rule.yaml",
        "rules/patternless-sca-rule.yaml",
    ],
)
def test_validation_of_valid_rules(run_fastlint_in_tmp: RunFastlint, rule):
    run_fastlint_in_tmp(
        rule,
        options=["--validate"],
        output_format=OutputFormat.TEXT,
        assert_exit_code=0,
    )
