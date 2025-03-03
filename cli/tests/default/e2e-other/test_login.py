import pytest
from tests.fastlint_runner import FastlintRunner

from fastlint.cli import cli
from fastlint.config_resolver import ConfigFile
from fastlint.config_resolver import ConfigLoader

expected_logout_str = "Logged out (log back in with `fastlint login`)\n"


# it should be ok to logout when not logged in and to logout twice
@pytest.mark.slow
def test_logout_not_logged_in(tmp_path, mocker):
    runner = FastlintRunner(
        env={"FASTLINT_SETTINGS_FILE": str(tmp_path / ".settings.yaml")},
    )
    result = runner.invoke(cli, subcommand="logout", args=[])
    assert result.exit_code == 0
    assert result.output == expected_logout_str

    # Logout twice should work
    result = runner.invoke(cli, subcommand="logout", args=[])
    assert result.exit_code == 0
    assert result.output == expected_logout_str


# it should fail when run from a non-terminal shell
@pytest.mark.slow
@pytest.mark.osemfail
def test_login_no_tty(tmp_path, mocker):
    runner = FastlintRunner(
        env={"FASTLINT_SETTINGS_FILE": str(tmp_path / ".settings.yaml")},
        # TODO: not sure why we need use_click_runner here, maybe
        # for the input=fake_key to work?
        use_click_runner=True,
    )
    fake_key = "key123"

    # Fail to login without a tty
    result = runner.invoke(
        cli,
        subcommand="login",
        args=[],
        input=fake_key,
    )
    assert result.exit_code == 2
    assert "fastlint login is an interactive command" in result.output


# it should login by using FASTLINT_APP_TOKEN
@pytest.mark.slow
@pytest.mark.osemfail
def test_login_env_token(tmp_path, mocker):
    runner = FastlintRunner(
        env={"FASTLINT_SETTINGS_FILE": str(tmp_path / ".settings.yaml")},
        use_click_runner=True,
    )
    fake_key = "key123"
    alt_key = "key456"

    # Patch Token Validation:
    mocker.patch(
        "fastlint.app.auth.get_deployment_from_token", return_value="deployment_name"
    )

    # Login with env token
    result = runner.invoke(
        cli,
        subcommand="login",
        args=[],
        env={"FASTLINT_APP_TOKEN": fake_key},
    )
    assert result.exit_code == 0
    assert result.output.startswith("Saved login token")
    assert "<redacted>" in result.output

    # Login should fail on second call
    result = runner.invoke(
        cli,
        subcommand="login",
        args=[],
        env={"FASTLINT_APP_TOKEN": alt_key},
    )
    assert result.exit_code == 2
    assert "API token already exists in" in result.output


# it should give access to the registry once logged in
@pytest.mark.slow
@pytest.mark.osemfail
def test_login_and_use_registry(tmp_path, mocker):
    runner = FastlintRunner(
        env={"FASTLINT_SETTINGS_FILE": str(tmp_path / ".settings.yaml")},
        use_click_runner=True,
    )
    fake_key = "key123"

    # Patch Token Validation:
    mocker.patch(
        "fastlint.app.auth.get_deployment_from_token", return_value="deployment_name"
    )

    result = runner.invoke(
        cli,
        subcommand="login",
        args=[],
        env={"FASTLINT_APP_TOKEN": fake_key},
    )
    assert result.exit_code == 0
    assert result.output.startswith("Saved login token")

    # Run p/ci
    result = runner.invoke(
        cli,
        args=["--config", "r/python.lang.correctness.useless-eqeq.useless-eqeq"],
    )
    assert (
        result.exit_code == 7
    ), "registry should refuse to send rules to invalid token"

    # Run policy with bad token -> no associated deployment_id
    result = runner.invoke(
        cli, args=["--config", "policy"], env={"FASTLINT_REPO_NAME": "test-repo"}
    )
    assert result.exit_code == 7
    assert "Invalid API Key" in result.output

    mocker.patch("fastlint.app.auth.get_deployment_id", return_value=1)

    # Run policy without FASTLINT_REPO_NAME
    result = runner.invoke(
        cli,
        args=["--config", "policy"],
    )
    assert result.exit_code == 7
    assert "Need to set env var FASTLINT_REPO_NAME" in result.output

    # Run policy. Check that request is made to correct deployment + org/repo
    mocked_config = mocker.patch.object(
        ConfigLoader,
        "_download_config_from_url",
        side_effect=lambda url: ConfigFile(None, "invalid-conifg}", url),
    )
    result = runner.invoke(
        cli, args=["--config", "policy"], env={"FASTLINT_REPO_NAME": "org/repo"}
    )
    assert result.exit_code == 7
    assert mocked_config.called
    assert "remote-registry_0 was not a mapping" in result.output
