from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Sequence

import fastlint.formatter.base as base
import fastlint.rpc_call
import fastlint.fastlint_interfaces.fastlint_output_v1 as out
from fastlint.error import FastlintError
from fastlint.rule import Rule
from fastlint.rule_match import RuleMatch


class GitlabSecretsFormatter(base.BaseFormatter):
    def format(
        self,
        rules: Iterable[Rule],
        rule_matches: Iterable[RuleMatch],
        fastlint_structured_errors: Sequence[FastlintError],
        cli_output_extra: out.CliOutputExtra,
        extra: Mapping[str, Any],
        ctx: out.FormatContext,
    ) -> str:
        output = base.to_CliOutput(
            rule_matches, fastlint_structured_errors, cli_output_extra
        )
        return fastlint.rpc_call.format(
            out.OutputFormat(out.GitlabSecrets()), ctx, output
        )
