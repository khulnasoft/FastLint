from enum import auto
from enum import Enum
from typing import List
from uuid import UUID

import click
from attrs import Factory
from attrs import frozen

from fastlint.app.session import AppSession
from fastlint.env import Env
from fastlint.error_handler import ErrorHandler
from fastlint.metrics import Metrics
from fastlint.fastlint_types import get_frozen_id
from fastlint.settings import Settings
from fastlint.terminal import Terminal
from fastlint.tracing import Traces


class DesignTreatment(Enum):
    LEGACY = auto()  # default
    SIMPLE = auto()  # simple output for product-focused users
    DETAILED = auto()  # detailed output for power users
    MINIMAL = auto()  # minimal output for pattern invocations


@frozen
class FastlintState:
    """
    An object click keeps around as custom global state for the current CLI invocation.

    This replaces the way we used to keep singletons around on the module level.
    """

    app_session: AppSession = Factory(AppSession)
    local_scan_id: UUID = get_frozen_id()
    env: Env = Factory(Env)
    metrics: Metrics = Factory(Metrics)
    error_handler: ErrorHandler = Factory(ErrorHandler)
    settings: Settings = Factory(Settings)
    terminal: Terminal = Factory(Terminal)
    traces: Traces = Factory(Traces)

    @staticmethod
    def get_cli_ux_flavor() -> DesignTreatment:
        """
        Returns the CLI UX flavor to use for the current CLI invocation.
        """
        # NOTE: First, check if the we enabled the new UX treatment via environment variable
        new_cli_ux = get_state().env.with_new_cli_ux
        if not new_cli_ux:
            return DesignTreatment.LEGACY
        # NOTE: Special case for pattern invocations
        if FastlintState.is_pattern_invocation():
            return DesignTreatment.MINIMAL
        config = get_config()
        # NOTE: We only support simple and detailed UX treatments for `fastlint scan` not `fastlint ci`
        if FastlintState.is_scan_invocation():
            # NOTE: Ignore the default 'auto' config and product flags such as 'supply-chain'
            has_config = bool(set(config) - {"auto", "supply-chain"})
            return DesignTreatment.DETAILED if has_config else DesignTreatment.SIMPLE
        return DesignTreatment.DETAILED

    @staticmethod
    def is_scan_invocation() -> bool:
        """
        Returns True iff the current CLI invocation is a scan invocation via `fastlint scan`.
        """
        ctx = get_context()
        command_name = ctx.command.name if hasattr(ctx, "command") else "unset"
        return command_name == "scan"

    @staticmethod
    def is_pattern_invocation() -> bool:
        """
        Returns True iff the current CLI invocation is a pattern invocation via `fastlint -e` or `fastlint --pattern`.
        """
        ctx = get_context()
        params = ctx.params if hasattr(ctx, "params") else {}
        return params.get("pattern") is not None


def get_context() -> click.Context:
    """
    Get the current CLI invocation's click context.
    """
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        # create a dummy context that will never be torn down
        from fastlint.cli import cli  # avoiding circular import

        ctx = click.Context(command=cli).scope().__enter__()

    return ctx


def get_config() -> List[str]:
    """
    Get the config passed via command line arguments (click)
    that is in turn passed to fastlint-core and friends.
    """
    ctx = get_context()
    params = ctx.params if hasattr(ctx, "params") else {}
    return list(params.get("config") or ())


def get_state() -> FastlintState:
    """
    Get the current CLI invocation's global state.
    """
    ctx = get_context()
    return ctx.ensure_object(FastlintState)
