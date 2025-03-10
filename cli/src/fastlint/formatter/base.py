import abc
from typing import Any
from typing import Collection
from typing import FrozenSet
from typing import Iterable
from typing import Mapping
from typing import Sequence

import fastlint.fastlint_interfaces.fastlint_output_v1 as out
from fastlint import __VERSION__
from fastlint.error import FastlintError
from fastlint.rule import Rule
from fastlint.rule_match import RuleMatch


# used also in ofastlint_sarif.py
def rule_match_to_CliMatch(rule_match: RuleMatch) -> out.CliMatch:
    extra = out.CliMatchExtra(
        message=rule_match.message,
        metadata=out.RawJson(rule_match.metadata),
        severity=rule_match.severity,
        fingerprint=rule_match.match_based_id,
        # 'lines' already contains '\n' at the end of each line
        lines="".join(rule_match.lines).rstrip(),
        metavars=rule_match.match.extra.metavars,
        dataflow_trace=rule_match.dataflow_trace,
        engine_kind=rule_match.match.extra.engine_kind,
        validation_state=rule_match.match.extra.validation_state,
        sca_info=rule_match.match.extra.sca_match,
    )

    if rule_match.extra.get("fixed_lines"):
        extra.fixed_lines = rule_match.extra.get("fixed_lines")
    if rule_match.fix is not None:
        extra.fix = rule_match.fix
    if rule_match.is_ignored is not None:
        extra.is_ignored = rule_match.is_ignored
    if rule_match.extra.get("extra_extra"):
        extra.extra_extra = out.RawJson(rule_match.extra.get("extra_extra"))

    return out.CliMatch(
        check_id=out.RuleId(rule_match.rule_id),
        path=out.Fpath(str(rule_match.path)),
        start=rule_match.start,
        end=rule_match.end,
        extra=extra,
    )


# used in json.py but now also in vim.py and emacs.py
def to_CliOutput(
    rule_matches: Iterable[RuleMatch],
    fastlint_structured_errors: Sequence[FastlintError],
    cli_output_extra: out.CliOutputExtra,
) -> out.CliOutput:
    # Sort according to RuleMatch.get_ordering_key
    sorted_findings = sorted(rule_matches)
    # Note that extra is not used here! Every part of the JSON output should
    # be specified in fastlint_output_v1.atd and be part of CliOutputExtra
    return out.CliOutput(
        version=out.Version(__VERSION__),
        results=[rule_match_to_CliMatch(rule_match) for rule_match in sorted_findings],
        errors=[error.to_CliError() for error in fastlint_structured_errors],
        paths=cli_output_extra.paths,
        time=cli_output_extra.time,
        explanations=cli_output_extra.explanations,
        interfile_languages_used=cli_output_extra.interfile_languages_used,
        skipped_rules=[],  # TODO: concatenate skipped_rules field from core responses
    )


class BaseFormatter(abc.ABC):
    def output(
        self,
        rules: FrozenSet[Rule],
        rule_matches: Sequence[RuleMatch],
        fastlint_structured_errors: Sequence[FastlintError],
        cli_output_extra: out.CliOutputExtra,
        extra: Mapping[str, Any],
        shown_severities: Collection[out.MatchSeverity],
        ctx: out.FormatContext,
    ) -> str:
        filtered_rules = (r for r in rules if r.severity in shown_severities)
        filtered_matches = (m for m in rule_matches if m.severity in shown_severities)
        return self.format(
            filtered_rules,
            filtered_matches,
            fastlint_structured_errors,
            cli_output_extra,
            extra,
            ctx,
        )

    @abc.abstractmethod
    def format(
        self,
        rules: Iterable[Rule],
        rule_matches: Iterable[RuleMatch],
        fastlint_structured_errors: Sequence[FastlintError],
        cli_output_extra: out.CliOutputExtra,
        extra: Mapping[str, Any],
        ctx: out.FormatContext,
    ) -> str:
        raise NotImplementedError

    def keep_ignores(self) -> bool:
        """
        Return True if ignored findings should be passed to this formatter; False otherwise.

        Ignored findings can still be distinguished using their _is_ignore property.
        """
        return False
