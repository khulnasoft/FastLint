import pytest
from tests.fastlint_runner import FastlintRunner

from fastlint.cli import cli


@pytest.mark.quick
@pytest.mark.parametrize("help_flag", ["--help", "-h"])
def test_help_text(tmp_path, snapshot, help_flag):
    """
    Test to make sure top level help text doesn't change unintentionally
    """
    runner = FastlintRunner(
        env={"FASTLINT_SETTINGS_FILE": str(tmp_path / ".settings.yaml")}
    )
    result = runner.invoke(cli, args=[help_flag], env={})
    snapshot.assert_match(result.output, "help.txt")
