import pytest
from tests.fixtures import RunFastlint

from fastlint.constants import OutputFormat


# Depending on the parameters, some tests pass with ofastlint or don't
# The actual test functions are split accordingly and call 'run_test_autofix'.
#
def run_test_autofix(
    run_fastlint_on_copied_files: RunFastlint,
    tmp_path,
    snapshot,
    rule,
    target,
    dryrun,
    output_format,
):
    rule = "rules/autofix/" + rule
    target = "autofix/" + target
    # Use run_fastlint_on_copied_files to prevent alteration of the
    # source-controlled test directory
    fastlint_result = run_fastlint_on_copied_files(
        rule,
        target_name=target,
        options=["--autofix", *(["--dryrun"] if dryrun else [])],
        output_format=output_format,
    )
    if output_format == OutputFormat.JSON:
        results_file = "results.json"
    else:
        results_file = "results.txt"
    snapshot.assert_match(
        fastlint_result.stdout,
        results_file,
    )

    if output_format == OutputFormat.TEXT:
        # TODO: is this essential?
        snapshot.assert_match(
            fastlint_result.stderr,
            "stderr.txt",
        )

    # Now make sure the files are actually updated
    with open(tmp_path / "targets" / target) as fd:
        result = fd.read()
    snapshot.assert_match(
        result,
        (f"{target}-dryrun" if dryrun else f"{target}-fixed"),
    )


# The rule is looked up in rules/autofix/ and the target in autofix/ but
# we use shorter names below so the snapshot dirs use less characters
# which can be an issue on Windows.
RULE_TARGET_PAIRS_JSON_OSEMPASS = [
    ("autofix.yaml", "autofix.py"),
    ("overlapping-collision.yaml", "collision.py"),
    ("python-assert-statement.yaml", "python-assert-statement.py"),
    ("python-ranges.yaml", "python-ranges.py"),
    ("replace-field-yaml.yaml", "replace-field-yaml.yaml"),
    ("three-autofixes.yaml", "three-autofixes.py"),
    ("java-string-wrap.yaml", "java-string-wrap.java"),
    ("exact-collision.yaml", "collision.py"),
    ("redundant.yaml", "redundant.py"),
    ("ocaml_paren_expr.yaml", "ocaml_paren_expr.ml"),
    ("python-delete-import.yaml", "python-delete-import.py"),
    ("two-autofixes.yaml", "two-autofixes.txt"),
    ("csv-writer.yaml", "csv-writer.py"),
    ("defaulthttpclient.yaml", "defaulthttpclient.java"),
    ("flask-use-jsonify.yaml", "flask-use-jsonify.py"),
    ("requests-use-timeout.yaml", "requests-use-timeout.py"),
    ("django-none-password-default.yaml", "django-none-password-default.py"),
    ("imported-entity.yaml", "imported-entity.py"),
    ("add-metadata-hcl.yaml", "add-metadata-hcl.hcl"),
    ("delete-partial-line.yaml", "delete-partial-line.py"),
    ("utf-8.yaml", "utf-8.py"),
]

# rule/target pairs for which ofastlint fails to produce the same JSON output
# as pyfastlint.
RULE_TARGET_PAIRS_JSON_OSEMFAIL = [
    # TODO: gives slightly different JSON output with ofastlint
    ("order.yaml", "order.py"),
]

# all rule/target pairs
RULE_TARGET_PAIRS = RULE_TARGET_PAIRS_JSON_OSEMPASS + RULE_TARGET_PAIRS_JSON_OSEMFAIL


# Check only the JSON output i.e. the correctness of the results rather
# than formatting.
@pytest.mark.kinda_slow
@pytest.mark.parametrize("dryrun", [True, False], ids=["dryrun", "not-dryrun"])
@pytest.mark.parametrize("output_format", [OutputFormat.JSON], ids=["json"])
@pytest.mark.parametrize("rule,target", RULE_TARGET_PAIRS_JSON_OSEMPASS)
def test_autofix_json_output(
    run_fastlint_on_copied_files: RunFastlint,
    tmp_path,
    snapshot,
    rule,
    target,
    dryrun,
    output_format,
):
    run_test_autofix(
        run_fastlint_on_copied_files,
        tmp_path,
        snapshot,
        rule,
        target,
        dryrun,
        output_format,
    )


# Same as above but gives different results between pyfastlint and ofastlint
@pytest.mark.osemfail
@pytest.mark.kinda_slow
@pytest.mark.parametrize("dryrun", [True, False], ids=["dryrun", "not-dryrun"])
@pytest.mark.parametrize("output_format", [OutputFormat.JSON], ids=["json"])
@pytest.mark.parametrize("rule,target", RULE_TARGET_PAIRS_JSON_OSEMFAIL)
def test_autofix_json_output_osemfail(
    run_fastlint_on_copied_files: RunFastlint,
    tmp_path,
    snapshot,
    rule,
    target,
    dryrun,
    output_format,
):
    run_test_autofix(
        run_fastlint_on_copied_files,
        tmp_path,
        snapshot,
        rule,
        target,
        dryrun,
        output_format,
    )


# Check only text output i.e. correctness of the findings + formatting
@pytest.mark.osemfail
@pytest.mark.kinda_slow
@pytest.mark.parametrize("dryrun", [True, False], ids=["dryrun", "not-dryrun"])
@pytest.mark.parametrize("output_format", [OutputFormat.TEXT], ids=["text"])
@pytest.mark.parametrize("rule,target", RULE_TARGET_PAIRS)
def test_autofix_text_output(
    run_fastlint_on_copied_files: RunFastlint,
    tmp_path,
    snapshot,
    rule,
    target,
    dryrun,
    output_format,
):
    run_test_autofix(
        run_fastlint_on_copied_files,
        tmp_path,
        snapshot,
        rule,
        target,
        dryrun,
        output_format,
    )
