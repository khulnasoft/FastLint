from typing import Iterator
from typing import List
from typing import Tuple

import fastlint.fastlint_interfaces.fastlint_output_v1 as out
from semdep.external.packaging.specifiers import InvalidSpecifier  # type: ignore
from semdep.external.packaging.specifiers import SpecifierSet  # type: ignore
from semdep.golang_version import compare_golang_specifier
from semdep.maven_version import compare_maven_specifier
from fastlint.error import FastlintError
from fastlint.fastlint_interfaces.fastlint_output_v1 import Ecosystem
from fastlint.fastlint_interfaces.fastlint_output_v1 import FoundDependency
from fastlint.fastlint_interfaces.fastlint_output_v1 import Gomod
from fastlint.fastlint_interfaces.fastlint_output_v1 import Maven


def is_in_range(ecosystem: Ecosystem, range: str, version: str) -> bool:
    if ecosystem == Ecosystem(Maven()):
        specifiers = [s.strip(" ") for s in range.split(",")]
        return all(compare_maven_specifier(s, version) for s in specifiers)
    elif ecosystem == Ecosystem(Gomod()):
        if len(version.split("-")) < 3:
            try:
                ss = SpecifierSet(range)
                matched = len(list(ss.filter([version]))) > 0
                return matched
            except InvalidSpecifier:
                raise FastlintError(
                    f"unknown package version comparison expression: {range}"
                )
        else:
            specifiers = [s.strip(" ") for s in range.split(",")]
            try:
                result = all(compare_golang_specifier(s, version) for s in specifiers)
            except Exception as e:
                raise FastlintError(
                    f"bad golang module version comparison between version {version} and spec range {range}: {e}"
                )

            return result
    else:
        try:
            ss = SpecifierSet(range)
            matched = len(list(ss.filter([version]))) > 0
            return matched
        except InvalidSpecifier:
            raise FastlintError(
                f"unknown package version comparison expression: {range}"
            )


# compare vulnerable range to version in lockfile
def dependencies_range_match_any(
    search_for_ranges: List[out.ScaPattern],
    have_deps: List[FoundDependency],
) -> Iterator[Tuple[out.ScaPattern, FoundDependency]]:
    for have_dep in have_deps:
        for target_range in search_for_ranges:
            if (
                target_range.ecosystem == have_dep.ecosystem
                and target_range.package == have_dep.package
                and is_in_range(
                    target_range.ecosystem, target_range.semver_range, have_dep.version
                )
            ):
                yield (target_range, have_dep)
