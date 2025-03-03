from pathlib import Path
from typing import Set

from attrs import frozen

import fastlint.fastlint_interfaces.fastlint_output_v1 as out
from fastlint.parsing_data import ParsingData


# This class exists to wrap some of the output returned by `fastlint-core`, on its way up
# through the call stack.
# This class is easily extendable if we want to add more information to the CLI output
# in the future.
@frozen
class OutputExtra:
    core: out.CoreOutput
    all_targets: Set[Path]
    parsing_data: ParsingData
