#
# Test target selection before any rule or language-specific filtering
#
import os
import shutil
import sys
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from pathlib import Path
from typing import List
from typing import Optional
from typing import Set

import pytest
from tests.fixtures import RunFastlint


# Specify how to download the test project
@dataclass
class GitProject:
    name: str
    # The git project URL (not the web page)
    url: str
    # SHA1 commit ID
    commit: str


# Identify how the repo should be set up and scanned by fastlint
class Config(Enum):
    # git: a git project scanned with the default fastlint options
    GIT = "git"

    # novcs: the same project from which '.git' was removed, scanned with
    # the default fastlint options
    NOVCS = "novcs"

    # ignoregit: run on the git project with the '--no-git-ignore' option
    # (does several things that are not obvious from its name)
    IGNOREGIT = "ignoregit"

    # default ignores: test a project that doesn't have .fastlintignore files
    GIT_DEFAULT_FASTLINTIGNORE = "git_default_fastlintignore"
    NOVCS_DEFAULT_FASTLINTIGNORE = "novcs_default_fastlintignore"

    # test a blank .fastlintignore
    GIT_EMPTY_FASTLINTIGNORE = "git_empty_fastlintignore"
    NOVCS_EMPTY_FASTLINTIGNORE = "novcs_empty_fastlintignore"

    # test --exclude options with an empty .fastlintignore
    GIT_EXCLUDE = "git_exclude"
    NOVCS_EXCLUDE = "novcs_exclude"

    # test --include options with an empty .fastlintignore
    GIT_INCLUDE = "git_include"
    NOVCS_INCLUDE = "novcs_include"


# The expectations regarding a particular target file path
@dataclass
class Expect:
    selected: bool
    selected_by_pyfastlint: Optional[bool] = None
    selected_by_ofastlint: Optional[bool] = None
    ignore_pyfastlint_result: bool = False
    ignore_ofastlint_result: bool = False
    paths: List[str] = field(default_factory=lambda: [])


# This is an artificial git project that offers all the difficulties we could
# think of for file targeting.
#
# Do we need to run on several projects?
PROJECT = GitProject(
    name="fastlint-test-project1",
    url="https://github.com/khulnasoft/fastlint-test-project1.git",
    commit="e0c5109b96ec52a5d972fc0bb96d60f1c343cfd9",
)


def is_git_project(config: Config) -> bool:
    if config is Config.GIT or config is Config.IGNOREGIT:
        return True
    else:
        return False


# Check whether a target path was selected or ignored by fastlint, depending
# the expectation we have.
def check_expectation(
    expect: Expect,
    is_running_ofastlint: bool,
    config: Config,
    selected_targets: Set[str],
):
    paths = expect.paths

    if is_running_ofastlint and expect.ignore_ofastlint_result:
        return
    if not is_running_ofastlint and expect.ignore_pyfastlint_result:
        return

    expect_selected = expect.selected
    if is_running_ofastlint and expect.selected_by_ofastlint is not None:
        expect_selected = expect.selected_by_ofastlint
    if not is_running_ofastlint and expect.selected_by_pyfastlint is not None:
        expect_selected = expect.selected_by_pyfastlint

    label = "[ofastlint]" if is_running_ofastlint else "[pyfastlint]"
    label = label + (f" [{config.value}]")
    for path in paths:
        # Sanity checks (important when checking that a path is not selected)
        if not os.path.lexists(path):
            raise Exception(f"path {path} doesn't exist in the file system!")
        # Tests
        if expect_selected:
            print(
                f"{label} check that target path was selected: {path}", file=sys.stderr
            )
            assert path in selected_targets
        else:
            print(
                f"{label} check that target path was ignored: {path}", file=sys.stderr
            )
            assert path not in selected_targets


# What we expect from fastlint when running with the most common invocation i.e.
#
# - run fastlint from the project root
# - run fastlint on the project root
# - no optional command-line flags
# - shared expectations in git and novcs projects
#
# To cover a new test case, add a file to the test repo and specify
# the expectations for the new path below.
#
COMMON_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            # Paths that are correctly selected by both pyfastlint and ofastlint
            ".gitignore",
            ".gitmodules",
            ".fastlintignore",
            "README.md",
            "gitignored-only-in-src-and-below.py",
            "gitignored-only-in-src.py",
            "hello.py",
            "img/hello.svg",
            "fastlintignored/hello.py",
            "fastlintignored-folder",
            "fastlintignored-only-in-src-and-below.py",
            "fastlintignored-only-in-src.py",
            "fastlintignored-py-contents/hello.rb",
            "src/.gitignore",
            "src/.hidden.py",
            "src/.fastlintignore",
            "src/10KiB.py",
            "src/hello.py",
            "src/fastlintignored-at-root/scanme",
            "src/fastlintignored-root",
            "src/fastlintignored-root-folder/hello.py",
            "src/fastlintignored-py-contents/hello.rb",
            "src/src/fastlintignored-anchored/hello.py",
            "src/subdir/gitignored-only-in-src.py",
            "src/subdir/fastlintignored-only-in-src.py",
            "tests/hello.py",
            # special characters in file names
            "src/~",
            "src/quote'/hello.py",
            "src/space !/hello.py",
            "src/🚀.py",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            # Paths that are correctly ignored by both pyfastlint and ofastlint
            "img/red.png",
            "fastlintignored-everywhere/hello.py",
            "fastlintignored-root",
            "fastlintignored-root-folder/hello.py",
            "src/broken-symlink.py",
            "src/fastlintignored-everywhere/hello.py",
            "src/fastlintignored-folder/hello.py",
            "src/fastlintignored-py-contents/hello.py",
            "src/symlink.py",
            "src/fastlintignored-via-include.py",
            "linux/link-to-file-in-dir-without-read-perm",
        ],
    ),
    # accepted differences between pyfastlint and ofastlint
    Expect(
        # excluded by ofastlint, selected by pyfastlint
        selected=False,
        selected_by_pyfastlint=True,
        paths=[
            # pyfastlint doesn't consult .fastlintignore files in subfolders:
            "src/fastlintignored-only-in-src-and-below.py",
            "src/fastlintignored-only-in-src.py",
        ],
    ),
    # pyfastlint bugs
    Expect(
        selected=False,
        selected_by_pyfastlint=True,
        paths=[
            "fastlintignored-py-contents/hello.py",
            "fastlintignored-at-root/ignoreme",
        ],
    ),
]

GIT_PROJECT_EXPECTATIONS = [
    # common expectations for a git project (but not for a novcs project)
    Expect(
        selected=False,
        paths=[
            # git submodule object (folder) listed by 'git ls-files'
            "submodules/fastlint-test-project2",
            # git submodule contents
            "submodules/fastlint-test-project2/hello.py",
        ],
    ),
    # accepted differences between pyfastlint and ofastlint
    Expect(
        selected=False,
        selected_by_pyfastlint=True,
        paths=[
            # pyfastlint doesn't consult .gitignore files
            # (except for the one included in the .fastlintignore file)
            "src/gitignored.py",
            "src/gitignored-only-in-src-and-below.py",
            "src/gitignored-only-in-src.py",
        ],
    ),
]

NOVCS_PROJECT_EXPECTATIONS = [
    # common expectations for a novcs project (but not for a git project)
    Expect(
        selected=True,
        paths=[
            # regular file in what was a git submodule
            "submodules/fastlint-test-project2/hello.py",
            # we don't consult .gitignore files in novcs projects
            "src/gitignored.py",
            "src/gitignored-only-in-src-and-below.py",
            "src/gitignored-only-in-src.py",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            "src/fastlintignored-via-include.py",
            # folder, not a regular file
            "submodules/fastlint-test-project2",
        ],
    ),
]

GIT_DEFAULT_FASTLINTIGNORE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            # sanity check
            "hello.py",
            # this is not ignored by the default fastlintignore patterns
            "fastlintignored/hello.py",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            # .git is excluded by 'git ls-files'
            ".git/HEAD",
            # tests/ is excluded by the default fastlintignore patterns
            "tests/hello.py",
            # git submodules are ignored
            "submodules/fastlint-test-project2/hello.py",
        ],
    ),
]

NOVCS_DEFAULT_FASTLINTIGNORE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            # sanity check
            "hello.py",
            # this is not ignored by the default fastlintignore patterns
            "fastlintignored/hello.py",
            # git submodules are not ignored
            "submodules/fastlint-test-project2/hello.py",
            # this is not ignored by the default fastlintignore patterns
            "submodules/fastlint-test-project2/fastlintignored/hello.py",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            # any .git file is excluded by the default fastlintignore patterns
            "submodules/fastlint-test-project2/.git",
            # tests/ is excluded by the default fastlintignore patterns
            "tests/hello.py",
            "submodules/fastlint-test-project2/tests/hello.py",
        ],
    ),
]

GIT_EMPTY_FASTLINTIGNORE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            "hello.py",
            "fastlintignored/hello.py",
            "tests/hello.py",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            # always excluded by git
            ".git/HEAD",
            # submodule, excluded by git
            "submodules/fastlint-test-project2/hello.py",
        ],
    ),
]

NOVCS_EMPTY_FASTLINTIGNORE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            "hello.py",
            "fastlintignored/hello.py",
            "tests/hello.py",
            "submodules/fastlint-test-project2/hello.py",
            "submodules/fastlint-test-project2/fastlintignored/hello.py",
            "submodules/fastlint-test-project2/tests/hello.py",
        ],
    ),
    # pyfastlint bugs
    Expect(
        selected=True,
        selected_by_pyfastlint=False,
        paths=[
            "submodules/fastlint-test-project2/.git",
        ],
    ),
]


GIT_EXCLUDE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            "hello.py",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            "fastlintignored-at-root/ignoreme",
            "fastlintignored-at-root2/ignoreme",
        ],
    ),
    # pyfastlint bugs
    Expect(
        selected=True,
        selected_by_pyfastlint=False,
        paths=[
            "src/fastlintignored-at-root/scanme",
            "src/fastlintignored-at-root2/scanme",
        ],
    ),
]


NOVCS_EXCLUDE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            "hello.py",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            "fastlintignored-at-root/ignoreme",
            "fastlintignored-at-root2/ignoreme",
        ],
    ),
    # pyfastlint bugs
    Expect(
        selected=True,
        selected_by_pyfastlint=False,
        paths=[
            "src/fastlintignored-at-root/scanme",
            "src/fastlintignored-at-root2/scanme",
        ],
    ),
]


# In the --include tests, the meanings of 'ignoreme' and 'scanme' are
# reversed, sorry about the confusion.
GIT_INCLUDE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            "fastlintignored-at-root/ignoreme",
            "fastlintignored-at-root2/ignoreme",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            "hello.py",
        ],
    ),
    # pyfastlint bugs
    Expect(
        selected=False,
        selected_by_pyfastlint=True,
        paths=[
            "src/fastlintignored-at-root/scanme",
            "src/fastlintignored-at-root2/scanme",
        ],
    ),
]


# In the --include tests, the meanings of 'ignoreme' and 'scanme' are
# reversed, sorry about the confusion.
NOVCS_INCLUDE_EXPECTATIONS = [
    Expect(
        selected=True,
        paths=[
            "fastlintignored-at-root/ignoreme",
            "fastlintignored-at-root2/ignoreme",
        ],
    ),
    Expect(
        selected=False,
        paths=[
            "hello.py",
        ],
    ),
    # pyfastlint bugs
    Expect(
        selected=False,
        selected_by_pyfastlint=True,
        paths=[
            "src/fastlintignored-at-root/scanme",
            "src/fastlintignored-at-root2/scanme",
        ],
    ),
]


@pytest.mark.kinda_slow
@pytest.mark.parametrize(
    # a list of extra fastlint CLI options and ofastlint-specific options
    "config,options,ofastlint_options,expectations",
    [
        (Config.GIT, [], [], COMMON_EXPECTATIONS + GIT_PROJECT_EXPECTATIONS),
        (Config.NOVCS, [], [], COMMON_EXPECTATIONS + NOVCS_PROJECT_EXPECTATIONS),
        (
            Config.IGNOREGIT,
            ["--no-git-ignore"],
            [],
            COMMON_EXPECTATIONS + NOVCS_PROJECT_EXPECTATIONS,
        ),
        (
            Config.GIT_DEFAULT_FASTLINTIGNORE,
            [],
            [],
            GIT_DEFAULT_FASTLINTIGNORE_EXPECTATIONS,
        ),
        (
            Config.NOVCS_DEFAULT_FASTLINTIGNORE,
            [],
            [],
            NOVCS_DEFAULT_FASTLINTIGNORE_EXPECTATIONS,
        ),
        (Config.GIT_EMPTY_FASTLINTIGNORE, [], [], GIT_EMPTY_FASTLINTIGNORE_EXPECTATIONS),
        (
            Config.NOVCS_EMPTY_FASTLINTIGNORE,
            [],
            [],
            NOVCS_EMPTY_FASTLINTIGNORE_EXPECTATIONS,
        ),
        (
            Config.GIT_EXCLUDE,
            [
                "--exclude",
                "/fastlintignored-at-root",
                "--exclude",
                "fastlintignored-at-root2/**",
            ],
            [],
            GIT_EXCLUDE_EXPECTATIONS,
        ),
        (
            Config.NOVCS_EXCLUDE,
            [
                "--exclude",
                "/fastlintignored-at-root",
                "--exclude",
                "fastlintignored-at-root2/**",
            ],
            [],
            NOVCS_EXCLUDE_EXPECTATIONS,
        ),
        (
            Config.GIT_INCLUDE,
            [
                "--include",
                "/fastlintignored-at-root",
                "--include",
                "fastlintignored-at-root2/**",
            ],
            [],
            GIT_INCLUDE_EXPECTATIONS,
        ),
        (
            Config.NOVCS_INCLUDE,
            [
                "--include",
                "/fastlintignored-at-root",
                "--include",
                "fastlintignored-at-root2/**",
            ],
            [],
            NOVCS_INCLUDE_EXPECTATIONS,
        ),
    ],
    ids=[
        Config.GIT.value,
        Config.NOVCS.value,
        Config.IGNOREGIT.value,
        Config.GIT_DEFAULT_FASTLINTIGNORE.value,
        Config.NOVCS_DEFAULT_FASTLINTIGNORE.value,
        Config.GIT_EMPTY_FASTLINTIGNORE.value,
        Config.NOVCS_EMPTY_FASTLINTIGNORE.value,
        Config.GIT_EXCLUDE.value,
        Config.NOVCS_EXCLUDE.value,
        Config.GIT_INCLUDE.value,
        Config.NOVCS_INCLUDE.value,
    ],
)
def test_project_target_selection(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    run_fastlint: RunFastlint,
    config: Config,
    options: List[str],
    ofastlint_options: List[str],
    expectations: List[Expect],
) -> None:
    project = PROJECT
    # Instead of copying or symlinking the git submodule that sits nicely
    # in our fastlint repo, we clone it as standalone repo to avoid problems
    # due to having the structure of a submodule but no parent git project.
    print(f"cd into {tmp_path}", file=sys.stderr)
    monkeypatch.chdir(tmp_path)
    print(f"clone {project.url}", file=sys.stderr)
    os.system(f"git clone {project.url} {project.name}")
    print(f"cd into {project.name}", file=sys.stderr)
    monkeypatch.chdir(Path(project.name))
    print(f"check out commit {project.commit}", file=sys.stderr)
    os.system(f"git checkout {project.commit}")
    print(f"check out submodules", file=sys.stderr)
    os.system(f"git submodule update --init --recursive")

    if (
        config is Config.NOVCS
        or config is Config.NOVCS_DEFAULT_FASTLINTIGNORE
        or config is Config.NOVCS_EMPTY_FASTLINTIGNORE
    ):
        print(f"remove .git to make this a no-VCS project", file=sys.stderr)
        shutil.rmtree(".git")

    if (
        config is Config.GIT_DEFAULT_FASTLINTIGNORE
        or config is Config.NOVCS_DEFAULT_FASTLINTIGNORE
        or config is Config.GIT_EMPTY_FASTLINTIGNORE
        or config is Config.NOVCS_EMPTY_FASTLINTIGNORE
        or config is Config.GIT_EXCLUDE
        or config is Config.NOVCS_EXCLUDE
        or config is Config.GIT_INCLUDE
        or config is Config.NOVCS_INCLUDE
    ):
        print(f"remove .fastlintignore files", file=sys.stderr)
        os.remove(".fastlintignore")
        os.remove("src/.fastlintignore")
        os.remove("submodules/fastlint-test-project2/.fastlintignore")
        if (
            config is Config.GIT_EMPTY_FASTLINTIGNORE
            or config is Config.NOVCS_EMPTY_FASTLINTIGNORE
            or config is Config.GIT_EXCLUDE
            or config is Config.NOVCS_EXCLUDE
            or config is Config.GIT_INCLUDE
            or config is Config.NOVCS_INCLUDE
        ):
            print(f"create an empty .fastlintignore", file=sys.stderr)
            open(".fastlintignore", "w").close()

    is_running_ofastlint = True if os.environ.get("PYTEST_USE_OFASTLINT") else False

    extra_options = options
    if is_running_ofastlint:
        extra_options += ofastlint_options

    # Call fastlint to list the target files and print them on stdout,
    # one per line.
    stdout, stderr = run_fastlint(
        # the '-e' and '--lang' options are to keep pyfastlint happy because
        # it wants to load rules
        options=["--x-ls", "-e", "hello", "--lang", "python"] + extra_options,
        assume_targets_dir=False,
        target_name=".",
    )
    selected_targets: Set[str] = set(filter(lambda x: x, stdout.split("\n")))

    print(f"selected target paths:", file=sys.stderr)
    for path in sorted(list(selected_targets)):
        print(f"  {path}", file=sys.stderr)

    # Check the status of each file path we want to check.
    for expect in expectations:
        check_expectation(expect, is_running_ofastlint, config, selected_targets)
