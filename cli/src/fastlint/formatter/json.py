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


class JsonFormatter(base.BaseFormatter):
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
        # alt: we could call json.dumps() directly here, but more consistent with
        # the other formatters to call instead rpc_call.format (this will also
        # help to avoid code duplication when we need to some post-processing of
        # the JSON output in osmegrep).
        # old: return json.dumps(output.to_json(), sort_keys=True, default=to_json)
        return fastlint.rpc_call.format(out.OutputFormat(out.Json()), ctx, output)
