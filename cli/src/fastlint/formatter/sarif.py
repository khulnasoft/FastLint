import contextlib
import json
import tempfile
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Sequence

import fastlint.formatter.base as base
import fastlint.rpc_call
import fastlint.fastlint_interfaces.fastlint_output_v1 as out
from fastlint.error import FastlintError
from fastlint.rule import Rule
from fastlint.rule_match import RuleMatch


class SarifFormatter(base.BaseFormatter):
    def keep_ignores(self) -> bool:
        return True

    # TODO? inline this function in the caller now that it's mostly a wrapper
    # over an RPC call
    def _ofastlint_format(
        self,
        rules: Iterable[Rule],
        cli_output: out.CliOutput,
        extra: Mapping[str, Any],
        ctx: out.FormatContext,
    ) -> Optional[str]:
        exit_stack = contextlib.ExitStack()
        with exit_stack:
            rule_file = exit_stack.enter_context(
                tempfile.NamedTemporaryFile("w+", suffix=".json")
            )
            rule_file_contents = json.dumps(
                {"rules": [rule._raw for rule in rules]}, indent=2, sort_keys=True
            )
            rule_file.write(rule_file_contents)
            rule_file.flush()
            rules_path = out.Fpath(rule_file.name)
            is_pro = bool(
                cli_output.engine_requested
                and cli_output.engine_requested == out.EngineKind(out.PRO_())
            )
            show_dataflow_traces = extra.get("dataflow_traces", False)
            sarif_fmt = out.SarifFormat(
                rules=rules_path,
                is_pro=is_pro,
                show_dataflow_traces=show_dataflow_traces,
            )
            formatted_output = fastlint.rpc_call.sarif_format(sarif_fmt, ctx, cli_output)
            if formatted_output:
                return formatted_output.value
        return None

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
        # LATER:return fastlint.rpc_call.format(out.OutputFormat(out.Sarif()),...)
        rule_list = list(rules)
        rpc_result = self._ofastlint_format(rule_list, output, extra, ctx)
        if rpc_result is not None:
            return rpc_result
        else:
            return "<ERROR: no SARIF output>"
