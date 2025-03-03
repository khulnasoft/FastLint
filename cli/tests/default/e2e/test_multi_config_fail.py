import pytest
from tests.fixtures import RunFastlint


# Running fastlint with multiple configs should fail fast if any of them have errors
@pytest.mark.kinda_slow
def test_multi_config_fail(run_fastlint_in_tmp: RunFastlint):
    run_fastlint_in_tmp(
        [
            "rules/multi_config_fail/error.yaml",
            "rules/multi_config_fail/no_error.yaml",
        ],
        target_name="basic/stupid.py",
        assert_exit_code=7,
    )
