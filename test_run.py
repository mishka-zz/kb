# SPDX-FileCopyrightText: 2026 Mike Volokhov
# SPDX-License-Identifier: BSD-2-Clause

"""The sample command under `kb.skel/run/`, held to the contract in the
`README.md` beside it.

The exit status is the whole of what a caller reads, so every verdict is
asserted as a status, from the command run as a process the way `kb stale`
runs it: from the project root, with the citation's path and name.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

RUN = Path(__file__).resolve().parent / "kb.skel" / "run"
SAMPLE = RUN / "run-program"
GREEN, RED, UNRUN = 0, 1, 77


def _command(*argv, cwd):
    done = subprocess.run([str(SAMPLE), *argv], cwd=cwd, capture_output=True, text=True)
    lines = done.stdout.strip().split("\n")
    return done.returncode, lines[-1]


def _test(root, at, script, executable=True):
    """A test that is a program: a shell script at ``at`` under ``root``."""
    path = root / at
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!/bin/sh\n{script}\n")
    path.chmod(0o755 if executable else 0o644)
    return path


def test_the_sample_is_executable_as_it_stands():
    assert os.access(SAMPLE, os.X_OK)


def test_the_probe_says_what_runs_the_tests_and_succeeds(tmp_path):
    code, said = _command("--probe", cwd=tmp_path)
    assert code == GREEN and said


@pytest.mark.parametrize("status, verdict, word", [
    (0, GREEN, "passed"), (77, UNRUN, "skipped"), (1, RED, "failed"), (3, 3, "failed")])
def test_the_programs_exit_status_is_the_verdict(tmp_path, status, verdict, word):
    _test(tmp_path, "app/checks/sum.test", f"echo noise\nexit {status}")
    code, said = _command("app/checks/sum.test", cwd=tmp_path)
    assert code == verdict
    assert said.startswith("app/checks/sum.test") and word in said


def test_a_name_is_handed_to_the_program_as_its_argument(tmp_path):
    _test(tmp_path, "app/checks/sum.test", '[ "$1" = carries ] || exit 1')
    assert _command("app/checks/sum.test", "carries", cwd=tmp_path)[0] == GREEN
    code, said = _command("app/checks/sum.test", "other", cwd=tmp_path)
    assert code == RED and "sum.test::other" in said


def test_the_program_runs_from_the_project_root(tmp_path):
    _test(tmp_path, "app/checks/here.test", '[ -d app/checks ] || exit 1')
    assert _command("app/checks/here.test", cwd=tmp_path)[0] == GREEN


def test_a_path_with_a_space_is_one_path(tmp_path):
    _test(tmp_path, "app/two words/sum.test", "exit 0")
    assert _command("app/two words/sum.test", cwd=tmp_path)[0] == GREEN


@pytest.mark.parametrize("at, made, executable, reason", [
    ("app/checks/gone.test", False, True, "is not there"),
    ("app/checks/flat.test", True, False, "is not executable"),
])
def test_what_cannot_run_is_red_and_says_why(tmp_path, at, made, executable, reason):
    """A test that ran nothing has not passed."""
    if made:
        _test(tmp_path, at, "exit 0", executable=executable)
    code, said = _command(at, cwd=tmp_path)
    assert code not in (GREEN, UNRUN) and reason in said


def test_asked_for_nothing_the_command_explains_itself_and_does_not_run(tmp_path):
    code, said = _command(cwd=tmp_path)
    assert code not in (GREEN, UNRUN) and "usage" in said
    code, said = _command("--help", cwd=tmp_path)
    assert code == GREEN and "usage" in said
