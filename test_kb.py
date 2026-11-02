# SPDX-FileCopyrightText: 2026 Mike Volokhov
# SPDX-License-Identifier: BSD-2-Clause

"""Every rule that refuses an entry, and proof that it fires.

The tool's promise is narrow - it never reads what a field says - so the whole
of its value is that the few things it *does* check cannot silently stop
checking. A rule nobody has watched fail is a rule that may already have
stopped: three of these were written after a review found the corresponding
check accepting what it was built to refuse.

Each test breaks exactly one thing and asserts the message names it.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load_module():
    spec = importlib.util.spec_from_file_location("kb_under_test", HERE / "kb.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["kb_under_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def kb(tmp_path, monkeypatch):
    """A miniature record, and the tool pointed at it."""
    module = _load_module()
    root = tmp_path / "kb"
    for place in module.QUEUE:
        (root / place).mkdir(parents=True)
    (root / "known" / "lib").mkdir(parents=True)
    (root / "known" / "status").mkdir(parents=True)
    (root / "archive").mkdir()
    # A record shaped like a project with two source trees, one of which may
    # be absent; nothing else, so a test that wants a document or a source
    # tree sets it itself.
    module.configure(root, {"owned": "app, lib, cmd, spec",
                            "outside": "app, lib, cmd", "theirs": "client",
                            "runners": RUNNERS})
    return module


#: The fixture's routing: a project running Python tests through one command
#: and Go tests through another, each named as that toolchain collects them.
RUNNERS = "test_*.py run-pytest, *_test.py run-pytest, *_test.go run-go-test"


def write(kb, place, identity, **fields):
    body = fields.pop("body", "prose")
    title = fields.pop("title", "a title")
    head = "".join(f"{k}: {v}\n" for k, v in fields.items())
    path = kb.ROOT / place / f"{identity}-slug.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nid: {identity}\ntitle: {title}\n{head}---\n\n{body}\n")
    return path


def faults(kb):
    return kb.check(*kb.load())


def sound(kb):
    """A record with one of everything, so a test breaks exactly one thing."""
    write(kb, "analyzed", "10", kind="work", criterion="something observable")
    write(kb, "known/lib", "11", kind="fact", provenance="judged: experience")
    write(kb, "known/decisions", "12", kind="decision", because="a reason")
    assert faults(kb) == []


# ------------------------------------------------------------ what parses

def test_a_file_with_no_fence_is_a_fault_and_not_a_silence(kb):
    (kb.ROOT / "noted" / "10-x.md").write_text("id: 10\ntitle: t\n")
    assert any("fence" in f for f in faults(kb))


def test_fields_that_are_never_closed_are_a_fault(kb):
    (kb.ROOT / "noted" / "10-x.md").write_text("---\nid: 10\ntitle: t\n")
    assert any("never closed" in f for f in faults(kb))


def test_a_head_line_that_is_neither_field_nor_prose_is_named(kb):
    (kb.ROOT / "noted" / "10-x.md").write_text("---\nid: 10\ntitle: t\nsee also 11\n---\n\nx\n")
    assert any("neither a field nor prose" in f for f in faults(kb))


def test_a_field_may_be_carried_on_indented_lines(kb):
    """An outcome is a paragraph by the time an entry closes.

    Held on one physical line it is unreadable in a diff and unreadable in the
    file, which is a cost paid on the fields most worth reading.
    """
    (kb.ROOT / "noted" / "10-x.md").write_text(
        "---\nid: 10\ntitle: t\ncriterion: the first part\n"
        "    and the rest of it\n---\n\nx\n"
    )
    entries, broken = kb.load()
    assert broken == []
    assert entries[0].fields["criterion"] == "the first part and the rest of it"


def test_a_carried_line_may_hold_a_colon_without_becoming_a_field(kb):
    """Which is why the indent is tested first.

    The fields this exists for are the ones that cite - a path and a line
    number, a test addressed with `::` - so a continuation reading as a new
    field would break it on exactly its own subject.
    """
    (kb.ROOT / "noted" / "10-x.md").write_text(
        "---\nid: 10\ntitle: t\ncriterion: measured at\n"
        "    app/tests/t.py:12\n---\n\nx\n"
    )
    entries, broken = kb.load()
    assert broken == []
    assert entries[0].fields["criterion"] == "measured at app/tests/t.py:12"
    assert "app" not in entries[0].fields


def test_an_indented_line_before_any_field_is_a_fault(kb):
    (kb.ROOT / "noted" / "10-x.md").write_text("---\n    stray\nid: 10\ntitle: t\n---\n\nx\n")
    assert any("indented under no field" in f for f in faults(kb))


def test_a_carried_line_that_lost_its_indent_is_a_fault_and_not_a_new_field(kb):
    """The one silent failure carrying a field could introduce, and it is shut.

    Unindented, `app/tests/t.py::name: ...` parses: a key with no
    space in it, then a colon. Against an open set of names it becomes a field
    nobody wrote, on the fields that carry citations - which is where a wrapped
    value is most likely in the first place. The set of names is closed, so it
    is a fault instead, and the message says what probably happened.
    """
    (kb.ROOT / "noted" / "10-x.md").write_text(
        "---\nid: 10\ntitle: t\noutcome: test: a thing\n"
        "app/tests/t.py::name is where it lives\n---\n\nx\n"
    )
    entries, broken = kb.load()
    assert any("not a field this format has" in f for f in broken)
    assert "app/tests/t.py" not in entries[0].fields


def test_a_misspelled_field_is_refused_rather_than_dropped(kb):
    """The same check from the other side.

    `critereon` used to leave an entry with no criterion and nothing anywhere
    saying so - the entry simply read as unshaped work.
    """
    write(kb, "analyzed", "10", kind="work", critereon="something observable")
    assert any("not a field this format has" in f for f in faults(kb))


def test_an_identity_outside_the_alphabet_is_refused_rather_than_crashing(kb):
    # `O` is excluded precisely because it is the typo a human makes, and an
    # entry carrying one used to leave `note` unable to hand out any identity.
    write(kb, "noted", "1O")
    assert any("not an identity" in f for f in faults(kb))
    kb.note(["a fresh thought"])


def test_an_id_its_own_filename_does_not_carry_is_a_fault(kb):
    path = write(kb, "analyzed", "10", kind="work", criterion="c")
    path.rename(path.with_name("99-slug.md"))
    assert any("its own name does not" in f for f in faults(kb))


def test_two_entries_may_not_hold_one_identity(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c")
    write(kb, "noted", "10")
    assert any("is already" in f for f in faults(kb))


def test_an_entry_in_a_queue_subdirectory_is_still_found(kb):
    write(kb, "noted/deeper", "10")
    assert [e.id for e in kb.load()[0]] == ["10"]


def test_a_file_directly_in_known_is_a_fault(kb):
    (kb.ROOT / "known" / "10-x.md").write_text("---\nid: 10\ntitle: t\nkind: fact\n---\n\nx\n")
    assert any("rather than under a subject" in f for f in faults(kb))


# -------------------------------------------------------------- the fields

def test_a_kind_outside_the_three_is_refused(kb):
    write(kb, "analyzed", "10", kind="opinion")
    assert any("is not one of" in f for f in faults(kb))


def test_shaped_work_with_no_criterion_is_refused(kb):
    write(kb, "analyzed", "10", kind="work")
    assert any("would show it done" in f for f in faults(kb))


def test_but_a_caught_thought_is_required_to_be_nothing_but_a_sentence(kb):
    write(kb, "noted", "10")
    assert faults(kb) == []


def test_a_decision_with_no_reasoning_is_refused(kb):
    write(kb, "known/decisions", "10", kind="decision")
    assert any("no reasoning to fail" in f for f in faults(kb))


def test_a_fact_with_no_provenance_is_refused(kb):
    write(kb, "known/lib", "10", kind="fact")
    assert any("where this is re-derived" in f for f in faults(kb))


def test_a_provenance_of_an_unknown_kind_is_refused(kb):
    """And the refusal says where the vocabulary is explained, because the
    wrong word is usually a summary where evidence was wanted - a reader who
    picked one needs the meaning, not just the list."""
    write(kb, "known/lib", "10", kind="fact", provenance="obviously: true")
    assert any("'obviously' is not one of" in f and "kb/schema.md" in f for f in faults(kb))


def test_a_terminal_entry_with_no_date_is_refused(kb):
    write(kb, "done", "10", kind="work", criterion="c", outcome="judged: it works")
    assert any("no date" in f for f in faults(kb))


def test_a_closure_with_no_outcome_is_refused(kb):
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-08-23")
    assert any("no outcome" in f for f in faults(kb))


def test_and_the_outcome_is_held_to_the_same_forms_as_a_provenance(kb):
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-08-23",
          outcome="obviously: done")
    assert any("'obviously' is not one of" in f for f in faults(kb))


def test_something_put_down_with_no_reason_is_refused(kb):
    write(kb, "refused", "10", kind="work", criterion="c", closed="2026-08-23")
    assert any("no because" in f for f in faults(kb))


def test_a_working_pointer_outside_the_archive_is_refused(kb):
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x",
          working="/etc/passwd")
    assert any("not in kb/archive" in f for f in faults(kb))


# ---------------------------------------------------------- what it points at

def test_a_provenance_naming_a_file_that_is_gone_is_refused(kb):
    (kb.REPO / "app").mkdir(parents=True)
    write(kb, "known/lib", "10", kind="fact",
          provenance="source: app/nowhere.py")
    assert any("which is not there" in f for f in faults(kb))


def test_a_provenance_naming_a_test_the_file_no_longer_holds_is_refused(kb):
    (kb.REPO / "app" / "tests").mkdir(parents=True)
    (kb.REPO / "app" / "tests" / "t.py").write_text("def test_here(): pass\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: app/tests/t.py::test_gone")
    assert any("does not define" in f for f in faults(kb))


def test_a_test_is_addressed_the_way_pytest_addresses_it_class_and_all(kb):
    # `stale` has to name the class, a bare test name living in more than one of
    # them; a checker that could not follow that refused its own format.
    (kb.REPO / "app" / "tests").mkdir(parents=True)
    (kb.REPO / "app" / "tests" / "t.py").write_text(
        "class TestFolding:\n    def test_here(self): pass\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: app/tests/t.py::TestFolding::test_here")
    assert faults(kb) == []


def test_but_a_class_the_file_does_not_hold_is_still_refused(kb):
    (kb.REPO / "app" / "tests").mkdir(parents=True)
    (kb.REPO / "app" / "tests" / "t.py").write_text(
        "class TestFolding:\n    def test_here(self): pass\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: app/tests/t.py::TestGone::test_here")
    assert any("TestGone" in f for f in faults(kb))


def test_a_citation_may_name_a_directory_and_is_not_read_as_a_file(kb):
    # A corpus is cited whole; opening it as a file is a crash and not a fault,
    # which is a different thing and stops the check dead.
    (kb.REPO / "app" / "datasets").mkdir(parents=True)
    write(kb, "known/lib", "10", kind="fact",
          provenance="measured: app/datasets, over every specimen in it")
    assert faults(kb) == []


def test_a_line_number_is_part_of_a_citation_and_not_part_of_the_path(kb):
    # `picks.py:82` is the form this project cites source in everywhere, and it
    # was once reported as a missing file.
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "picks.py").write_text("x = 1\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="source: app/picks.py:82")
    assert faults(kb) == []


def test_prose_naming_something_the_file_no_longer_holds_is_refused_too(kb):
    """The half that catches an open entry. Nothing re-runs one, and its body is
    where it says what some function does - so a name written there is the only
    thing about it that can be checked mechanically."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "geometry.py").write_text("def _split_record(): pass\n")
    write(kb, "analyzed", "10", kind="work", criterion="c",
          body="what it costs is app/geometry.py::_split_header")
    assert any("does not define" in f for f in faults(kb))


def test_a_citation_no_path_reaches_is_refused(kb):
    """It wears the strongest form in the record and is the emptiest thing in
    it: nothing checks the name, and `stale` never runs the test."""
    (kb.REPO / "app" / "tests").mkdir(parents=True)
    (kb.REPO / "app" / "tests" / "t.py").write_text("def test_here(): pass\n")
    write(kb, "known/lib", "10", kind="fact", provenance="test: t.py::test_here")
    assert any("no path reaches" in f for f in faults(kb))


def test_and_so_is_one_that_left_the_file_to_the_sentence_before(kb):
    """`…t.py::TestOne::test_a, and ::test_b` - the second reads as evidence
    and is reached by nothing."""
    (kb.REPO / "app" / "tests").mkdir(parents=True)
    (kb.REPO / "app" / "tests" / "t.py").write_text(
        "def test_here(): pass\ndef test_there(): pass\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: app/tests/t.py::test_here, and ::test_there")
    assert any("no path reaches" in f for f in faults(kb))


def test_but_a_namespace_is_not_a_citation(kb):
    """`::` is also how C++ spells a scope and how a doc comment reaches a
    method. What separates a citation is that it names a file."""
    write(kb, "known/lib", "10", kind="fact",
          provenance="judged: a std::vector, and header::Field beside it")
    assert faults(kb) == []


def test_nor_is_one_in_prose_where_the_file_is_the_sentence_around_it(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c",
          body="the parser answers header::Field and part::Tree differently")
    assert faults(kb) == []


def test_a_name_that_is_only_part_of_another_is_still_gone(kb):
    """Read as a substring, `::split_rec` passes on a file holding
    `_split_record`, and the citation says nothing while looking exact."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="source: app/g.py::split_rec")
    assert any("does not define" in f for f in faults(kb))


def test_a_field_that_is_not_provenance_is_read_the_same_way(kb):
    """A criterion naming the population it is checked over is a citation like
    any other, and it was the reason for reading every field."""
    (kb.REPO / "app").mkdir(parents=True)
    write(kb, "analyzed", "10", kind="work",
          criterion="every specimen in app/tests/gone.py is held")
    assert any("which is not there" in f for f in faults(kb))


def test_prose_about_a_file_that_has_gone_is_not_a_fault(kb):
    """A body saying something was deleted names a path that is rightly not
    there - and it may name what was in it, which is the same sentence."""
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-08-25",
          outcome="judged: done",
          body="app/legacy/parse.py::unfold went with the prototype")
    assert faults(kb) == []


def test_a_bare_path_in_prose_is_prose_and_not_a_citation(kb):
    """The record's subject includes what has been *deleted*, and a sentence
    saying so names a path that is rightly not there. Evidence is read the other
    way: a `provenance` naming a file that is gone is a fault, above."""
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-08-24",
          outcome="judged: done", body="app/legacy/ is deleted")
    assert faults(kb) == []


def test_a_citation_into_a_repository_that_is_not_here_is_passed_over(kb):
    """A tree released on its own cadence may not be cloned here at all. A
    reader without one is not holding a stale record, and a page of faults
    about it would bury the ones that are theirs."""
    write(kb, "known/lib", "10", kind="fact",
          provenance="source: cmd/serve.go::Serve")
    assert faults(kb) == []


def test_but_a_repository_that_is_here_is_read_like_any_other_tree(kb):
    """One repository arriving says nothing about the others, so it must not
    switch the check on for them."""
    (kb.REPO / "cmd").mkdir(parents=True)
    write(kb, "known/lib", "10", kind="fact",
          provenance="source: cmd/serve.go::Serve")
    write(kb, "known/lib", "11", kind="fact",
          provenance="source: lib/parse.go::unfold")
    said = faults(kb)
    assert any("cmd/serve.go" in f for f in said)
    assert not any("lib/parse.go" in f for f in said)


def test_a_directory_gone_from_a_repository_that_is_here_still_fails(kb):
    """The excuse is the whole tree being absent, never anything below it. Asked
    one level down, a deleted subdirectory would read as a repository nobody
    cloned and its citations would go quiet."""
    (kb.REPO / "app").mkdir(parents=True)
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: app/tests/gone.py::test_here")
    assert any("app/tests/gone.py" in f for f in faults(kb))


def test_a_related_that_leads_nowhere_is_refused(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c", related="99")
    assert any("leads nowhere" in f for f in faults(kb))


def test_a_citation_from_outside_the_record_is_resolved_too(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c", body="see [[99]]")
    assert any("[[99]] leads nowhere" in f for f in faults(kb))


def test_a_bracketed_word_that_is_not_an_identity_is_left_alone(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c", body="see [[TODO]] and [[FIXME]]")
    assert faults(kb) == []


def test_a_field_written_twice_is_a_fault_and_not_a_silence(kb):
    """The second replaces the first, so a closure written with one `outcome`
    per kind of evidence keeps the last and loses the rest - and what it loses
    reaches neither `check` nor `stale`."""
    path = write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-07",
                 outcome="judged: the last one")
    path.write_text(path.read_text().replace(
        "outcome: judged: the last one",
        "outcome: test: app/t.py::gone\noutcome: judged: the last one"))
    assert any("written twice" in f for f in faults(kb))


# ------------------------------------------------ a citation, wherever it stands

def test_a_caught_thought_s_fields_are_held_to_their_citations(kb):
    """`noted/` promises nothing about which fields are there and everything
    about what they name."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "noted", "10", tags="the scan at app/g.py::_split_header")
    assert any("does not define" in f for f in faults(kb))


def test_a_caught_thought_s_prose_is_held_too(kb):
    """It is where an entry sits longest, so it is where a citation has the
    most time to go stale unnoticed."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "noted", "10", body="app/g.py::_split_header is where")
    assert any("does not define" in f for f in faults(kb))


def test_a_title_is_read_with_the_body_and_not_with_the_fields(kb):
    """`note` writes the caught sentence as both, so a citation lands in the
    title first - and a missing file is prose there for the same reason it is
    prose in a body."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "noted", "10", title="app/g.py::_split_header is asked once")
    assert any("does not define" in f for f in faults(kb))
    write(kb, "noted", "11", title="app/gone.py::_split_record went with it")
    assert not any("11-slug" in f for f in faults(kb))


def test_a_citation_in_prose_is_held_to_the_form_as_a_field_is(kb):
    """One form, because a basename resolves only while one file carries it -
    and a tree easily holds a `specification.md` under several `doc/` trees."""
    write(kb, "analyzed", "10", kind="work", criterion="c",
          body="what it costs is g.py::_split_record")
    assert any("no path reaches" in f for f in faults(kb))


def test_and_so_is_a_title(kb):
    write(kb, "noted", "10", title="header.go::unfold is asked once a field")
    assert any("no path reaches" in f for f in faults(kb))


def test_a_fenced_block_is_quoted_rather_than_claimed(kb):
    """A body pasting a test address is pasting a command that runs from the
    repository, and one about citations has to be able to write the form it is
    about. Neither claims a name is there."""
    write(kb, "analyzed", "10", kind="work", criterion="c",
          body="run it:\n\n```\ntests/t.py::TestOne::test_a\n```\n")
    assert faults(kb) == []


def test_a_fence_may_be_written_with_tildes(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c",
          body="run it:\n\n~~~\ntests/t.py::TestOne::test_a\n~~~\n")
    assert faults(kb) == []


def test_a_fence_nobody_closed_swallows_nothing(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c",
          body="run it:\n\n```\ntests/t.py::TestOne::test_a\n")
    assert any("no path reaches" in f for f in faults(kb))


def test_a_citation_broken_after_the_colons_is_a_fault(kb):
    """The path alone matches and the file is there, so the name goes unread -
    and the way to write one is to wrap a long citation, which every field
    carried on an indented line is."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "analyzed", "10", kind="work",
          criterion="held by app/g.py::\n    _split_header")
    assert any("breaks before the name" in f for f in faults(kb))


def test_a_closed_entry_s_prose_is_reported_rather_than_refused(kb):
    """It carries a date, and its body is what was true on it. Failing the run
    is pressure to repoint the path, which is backdating - and where the
    entry's own work replaced what it diagnosed, repointing writes a false
    statement about today's code in the record's strongest form."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-07",
          outcome="judged: done", body="it cost app/g.py::_split_header")
    entries = kb.load()[0]
    assert kb.check(entries, []) == []
    assert any("does not define" in line for line in kb.moved_under(entries))


def test_but_a_closed_entry_is_still_held_to_the_form(kb):
    """Only the name-still-defined half is a report there. A citation no path
    reaches was unreadable on the day it was written too."""
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-07",
          outcome="judged: done", body="it cost g.py::_split_record")
    assert any("no path reaches" in f for f in faults(kb))


def test_and_its_evidence_is_refused_wherever_it_stands(kb):
    """An `outcome` is what a reader is sent to and what `stale` runs, so it is
    held whatever the place."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-07",
          outcome="source: app/g.py::_split_header")
    assert any("does not define" in f for f in faults(kb))


def test_the_run_says_what_the_code_has_moved_under(kb, capsys, monkeypatch):
    """The listing is the whole of what a closed entry gets, so a run that
    computes it and prints nothing is the same as not checking at all."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    (kb.ROOT / kb.PROJECT).write_text("---\nowned: app\n---\n")
    monkeypatch.setenv("KB_RECORD", str(kb.ROOT))
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-07",
          outcome="judged: done", body="it cost app/g.py::_split_header")
    assert kb.main(["kb.py", "check"]) == 0
    said = capsys.readouterr().out
    assert "_split_header" in said
    assert "walkable" not in said


def test_a_subject_named_like_a_terminal_place_is_not_one(kb):
    """`place` is the directory's name, and `known/` holds whatever subjects
    somebody made. Only the queue has terminal places in it."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    write(kb, "known/done", "10", kind="fact", provenance="judged: it works",
          body="it cost app/g.py::_split_header")
    assert any("does not define" in f for f in faults(kb))


def test_a_document_read_for_what_is_true_now_is_held_like_an_entry(kb, monkeypatch):
    """`load` walks the entries and nothing walked these, so a citation in the
    document a reader opens first was held to nothing at all."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def _split_record(): pass\n")
    monkeypatch.setattr(kb, "DOCUMENTS", ("kb/SKILL.md",))
    sound(kb)
    (kb.ROOT / "SKILL.md").write_text("see app/g.py::_split_header\n")
    assert any("does not define" in f for f in faults(kb))


# --------------------------------------------- what "defines" means, by language

def test_a_crossed_class_and_test_is_refused(kb):
    """Both halves exist and pytest collects neither, which is the shape a
    rename leaves behind - and `stale` would then run nothing."""
    (kb.REPO / "app" / "tests").mkdir(parents=True)
    (kb.REPO / "app" / "tests" / "t.py").write_text(
        "class TestOne:\n    def test_a(self): pass\n\n\n"
        "class TestTwo:\n    def test_b(self): pass\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="source: app/tests/t.py::TestOne::test_a")
    assert faults(kb) == []
    write(kb, "known/lib", "11", kind="fact",
          provenance="source: app/tests/t.py::TestOne::test_b")
    assert any("does not define" in f for f in faults(kb))


def test_but_a_bare_test_name_is_a_name_in_the_file(kb):
    """`stale` looks the class up, so a bare name is a claim that the file
    holds the name and nothing about where."""
    (kb.REPO / "app" / "tests").mkdir(parents=True)
    (kb.REPO / "app" / "tests" / "t.py").write_text(
        "class TestOne:\n    def test_a(self): pass\n")
    write(kb, "known/lib", "10", kind="fact",
          provenance="source: app/tests/t.py::test_a")
    assert faults(kb) == []


def test_a_name_bound_in_a_fixture_the_file_quotes_is_not_defined_by_it(kb):
    """A column-zero pattern matches inside a triple-quoted fixture, which is
    exactly where a test file quotes a configuration."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text('CONFIG = """\nwindow = 512\n"""\n')
    write(kb, "known/lib", "10", kind="fact", provenance="source: app/g.py::window")
    assert any("does not define" in f for f in faults(kb))


def test_but_a_name_bound_beside_another_is(kb):
    """`NANO, EDGE = ...` binds two names no pattern of the form `^name =`
    reaches."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("NANO, EDGE = 4, 8\n")
    write(kb, "known/lib", "10", kind="fact", provenance="source: app/g.py::EDGE")
    assert faults(kb) == []


def test_and_so_is_one_written_under_a_branch_the_module_takes(kb):
    """A class under `if TYPE_CHECKING` is written in that module. One inside a
    function is not: nothing outside can reach it."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text(
        "if True:\n    class Table:\n        def fill(self): pass\n\n\n"
        "def outer():\n    class Hidden: pass\n")
    write(kb, "known/lib", "10", kind="fact", provenance="source: app/g.py::Table.fill")
    assert faults(kb) == []
    write(kb, "known/lib", "11", kind="fact", provenance="source: app/g.py::Hidden")
    assert any("does not define" in f for f in faults(kb))


def test_a_method_is_written_inside_its_class_and_not_merely_beside_it(kb):
    """`Class.method` is the other way prose names something. Asked as two
    independent names it passes on a file holding both in different classes,
    which is the case the dot is there to exclude."""
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text(
        "class One:\n    def redraw(self): pass\n\n\nclass Two:\n    def other(self): pass\n")
    write(kb, "known/lib", "10", kind="fact", provenance="source: app/g.py::One.redraw")
    assert faults(kb) == []
    write(kb, "known/lib", "11", kind="fact", provenance="source: app/g.py::Two.redraw")
    assert any("does not define" in f for f in faults(kb))


def test_a_go_name_mentioned_in_a_doc_comment_is_not_defined_by_the_file(kb):
    """The day a function leaves a file, the file names its new home in a
    comment - which is the one event the citation exists to catch, and the one
    a word match survives."""
    (kb.REPO / "lib").mkdir(parents=True)
    (kb.REPO / "lib" / "h.go").write_text(
        "// unfold moved to fold.go; see unfold there.\nfunc fold(s string) string { return s }\n")
    write(kb, "known/lib", "10", kind="fact", provenance="source: lib/h.go::unfold")
    assert any("does not define" in f for f in faults(kb))
    write(kb, "known/lib", "11", kind="fact", provenance="source: lib/h.go::fold")
    assert not any("11-slug" in f for f in faults(kb))


def test_a_go_method_is_written_on_its_type(kb):
    (kb.REPO / "lib").mkdir(parents=True)
    (kb.REPO / "lib" / "h.go").write_text(
        "type Part struct{ name string }\n\nfunc (p *Part) Walk() {}\n\ntype Tree struct{}\n")
    write(kb, "known/lib", "10", kind="fact", provenance="source: lib/h.go::Part.Walk")
    write(kb, "known/lib", "11", kind="fact", provenance="source: lib/h.go::Part::Walk")
    assert faults(kb) == []
    write(kb, "known/lib", "12", kind="fact", provenance="source: lib/h.go::Tree.Walk")
    assert any("Tree.Walk" in f and "does not define" in f for f in faults(kb))


def test_a_go_method_is_written_where_its_func_is_whichever_file_declares_its_type(kb):
    """Go lets a method sit in any file of its type's package, so `Type.Method`
    claims the method and not the type: the file writing the func is the one it
    names. A field is written where the type is, and is held there, and what
    follows a method is held to the word as it is after any other."""
    (kb.REPO / "lib").mkdir(parents=True)
    (kb.REPO / "lib" / "graph.go").write_text("type Graph struct {\n\tcur int\n}\n")
    (kb.REPO / "lib" / "compile.go").write_text(
        'func (g *Graph) Current() string { return "" }\n')
    write(kb, "known/lib", "10", kind="fact", provenance="source: lib/compile.go::Graph.Current")
    write(kb, "known/lib", "11", kind="fact", provenance="source: lib/graph.go::Graph.cur")
    assert faults(kb) == []
    write(kb, "known/lib", "12", kind="fact", provenance="source: lib/graph.go::Graph.Current")
    write(kb, "known/lib", "13", kind="fact", provenance="source: lib/compile.go::Graph.cur")
    write(kb, "known/lib", "14", kind="fact",
          provenance="source: lib/compile.go::Graph.Current.gone")
    found = faults(kb)
    assert any("Graph.Current, which lib/graph.go does not define" in f for f in found)
    assert any("Graph.cur, which lib/compile.go does not define" in f for f in found)
    assert any("Graph.Current.gone, which" in f for f in found)


def test_a_go_method_and_a_member_of_a_generic_type_are_written_on_it(kb):
    """A receiver carries its type's parameters, and the type declares them,
    constraints and all."""
    (kb.REPO / "lib").mkdir(parents=True)
    (kb.REPO / "lib" / "ring.go").write_text(
        "type ring[T any] struct {\n\tsink T\n}\n\n"
        "func (t *ring[T]) Publish(v T) {}\n\n"
        "type pair[K comparable, V ~[]byte] interface {\n\tGet(K) V\n}\n")
    for identity, name in (("10", "ring.Publish"), ("11", "ring.sink"),
                           ("12", "pair.Get")):
        write(kb, "known/lib", identity, kind="fact", provenance=f"source: lib/ring.go::{name}")
    assert faults(kb) == []
    write(kb, "known/lib", "13", kind="fact", provenance="source: lib/ring.go::ring.Close")
    assert any("ring.Close" in f and "does not define" in f for f in faults(kb))


def test_a_go_struct_field_and_a_grouped_constant_are_declared_where_their_block_is(kb):
    (kb.REPO / "lib").mkdir(parents=True)
    (kb.REPO / "lib" / "h.go").write_text(
        "const (\n\tMinWidth = 3\n\tMaxWidth = 8\n)\n\n"
        "type Shape struct {\n\tCorners int\n}\n\n"
        "func Map[T any](xs []T) []T { return xs }\n")
    for identity, name in (("10", "MaxWidth"), ("11", "Shape.Corners"), ("12", "Map")):
        write(kb, "known/lib", identity, kind="fact",
              provenance=f"source: lib/h.go::{name}")
    assert faults(kb) == []
    write(kb, "known/lib", "13", kind="fact", provenance="source: lib/h.go::MaxHeight")
    assert any("MaxHeight" in f for f in faults(kb))


def test_a_go_subtest_is_held_to_the_word_beside_its_test(kb):
    """Go declares a subtest nowhere - `t.Run` takes a string - so what follows
    a test function is held to the word, as it was before."""
    (kb.REPO / "lib").mkdir(parents=True)
    (kb.REPO / "lib" / "h_test.go").write_text(
        'func TestUnfold(t *testing.T) {\n\tt.Run("folded_across_lines", nil)\n}\n')
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: lib/h_test.go::TestUnfold::folded_across_lines")
    assert faults(kb) == []
    write(kb, "known/lib", "11", kind="fact",
          provenance="test: lib/h_test.go::TestUnfold::gone")
    assert any("does not define" in f for f in faults(kb))


# ------------------------------------------------- split, merge and the queue

def test_a_citation_survives_a_split(kb):
    assert kb.resolves("12", {"12.1", "12.2"})


def test_and_survives_a_merge(kb):
    assert kb.resolves("12.1", {"12"})


def test_but_never_lands_on_an_unrelated_sibling(kb):
    # Going up must look for that parent itself, never for whatever else is
    # left of its family - otherwise a reader is sent somewhere plausible and
    # wrong, and nothing says so.
    assert not kb.resolves("35.7", {"35.1"})
    assert not kb.resolves("99.4", {"98"})


def test_a_measurement_must_defend_a_number_somebody_claims(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c", tags="measurement")
    assert any("defending no stated number" in f for f in faults(kb))


def test_and_is_admitted_once_it_names_one(kb):
    write(kb, "known/status", "11", kind="fact", provenance="gate: a gate")
    write(kb, "analyzed", "10", kind="work", criterion="c", tags="measurement", related="11")
    assert faults(kb) == []


def test_a_closed_fault_may_not_still_be_marked_quiet(kb):
    write(kb, "done", "10", kind="work", criterion="c", tags="quiet",
          outcome="judged: it works", closed="2026-08-26")
    assert any("quiet on a done entry" in f for f in faults(kb))


def test_but_an_open_one_may(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c", tags="quiet")
    assert faults(kb) == []


def test_and_so_may_a_limit_that_was_measured_stated_and_left(kb):
    # The exception is the whole of the nesting: a fact under known/ can hold
    # the mark for a limit nobody intends to fix, where a closed fault cannot.
    write(kb, "known/ours", "11", kind="fact", provenance="judged: it works", tags="quiet")
    assert faults(kb) == []


# --------------------------------------------------------------------- note

def test_a_wrapped_paragraph_cannot_write_fields_nobody_typed(kb):
    kb.note(["the fold reads backwards\nkind: fact\nprovenance: judged: obviously true\nand on"])
    entry = kb.load()[0][0]
    assert entry.fields.get("kind") is None
    assert entry.fields.get("provenance") is None
    assert "obviously true" in entry.body


def test_a_title_is_not_cut_at_the_first_full_stop(kb):
    kb.note(["the retry at 0.5 s reads the deadline backwards"])
    assert "0.5 s" in kb.load()[0][0].title


def test_a_long_sentence_keeps_its_end(kb):
    """The tail of a caught thought is what was noticed in it, so a title is
    the whole sentence however long. The filename is what needs a bound."""
    sentence = " ".join(["a long thought"] * 20)
    kb.note([sentence])
    entry = kb.load()[0][0]
    assert entry.title == sentence
    assert len(entry.path.name) < 80


# ------------------------------------------------------- finished, not moved

def test_an_entry_carrying_an_outcome_in_the_queue_is_surfaced(kb):
    """Closing is written before the file moves, so there is a window where an
    entry is finished and the directory does not know it. Nobody looking at the
    queue can see that."""
    write(kb, "scoped", "10", kind="work", criterion="c", outcome="judged: it holds")
    assert [e.id for e in kb.worked_through(kb.load()[0])] == ["10"]


def test_and_it_is_a_prompt_rather_than_a_fault(kb):
    """There are good reasons to hold one open - a second reader who has not
    been through it, a test tier not yet run - and the entry's prose is where
    they belong. So this must not fail the run."""
    write(kb, "scoped", "10", kind="work", criterion="c", outcome="judged: it holds")
    entries, broken = kb.load()
    assert kb.check(entries, broken) == []


def test_a_closed_date_counts_as_much_as_an_outcome(kb):
    """`moot/` and `refused/` are reached with `because` and `closed` rather
    than with an outcome, so the date is the signal there."""
    write(kb, "analyzed", "10", kind="decision", because="b", closed="2026-08-23")
    assert [e.id for e in kb.worked_through(kb.load()[0])] == ["10"]


def test_an_entry_that_has_moved_is_not_surfaced_again(kb):
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-08-23",
          outcome="judged: it holds")
    assert kb.worked_through(kb.load()[0]) == []


def test_nor_is_work_that_is_merely_open(kb):
    write(kb, "scoped", "10", kind="work", criterion="c")
    write(kb, "noted", "11")
    assert kb.worked_through(kb.load()[0]) == []


# ------------------------------------------------ what the standing hint says

def _shown(kb, capsys, **tagged):
    for identity, tags in tagged.items():
        write(kb, "analyzed", identity, kind="work", criterion="c", tags=tags)
    kb.state(kb.load()[0], [], limit=1)
    return capsys.readouterr().out


def test_the_cut_the_hint_offers_is_one_the_queue_can_make(kb, capsys):
    """Naming a subject the record does not hold sends the reader to an empty
    list, which reads as nothing being open rather than as a bad guess."""
    out = _shown(kb, capsys, **{"10": "cache", "11": "cache, network", "12": "network"})
    assert "--field place=analyzed, and any tag narrows it: --field tags=cache" in out


def test_and_it_is_the_one_that_cuts_least(kb, capsys):
    """A tag one entry carries hides the rest, so the hint would demonstrate the
    option by throwing away the list it is offered on."""
    out = _shown(kb, capsys, **{"10": "network", "11": "network", "12": "cache"})
    assert "--field tags=network" in out


def test_a_mark_is_not_offered_as_a_cut(kb, capsys):
    """`release`, `quiet` and `needs-human` are printed against every row
    already, so cutting by one shows the reader what they are looking at."""
    out = _shown(kb, capsys, **{"10": "release", "11": "quiet, release", "12": "quiet"})
    assert "--field tags=" not in out
    assert "--field place=analyzed" in out


def test_an_untagged_queue_still_gets_a_whole_command(kb, capsys):
    out = _shown(kb, capsys, **{"10": "", "11": "", "12": ""})
    assert "kb find --field place=analyzed\n" in out


def test_a_marked_thought_is_not_buried_under_older_ones(kb, capsys):
    """Caught last and able to return a wrong number quietly is what the next
    session has to see first, and oldest first put it behind the cut."""
    write(kb, "noted", "10", noted="2026-08-01")
    write(kb, "noted", "11", noted="2026-08-02")
    write(kb, "noted", "12", noted="2026-09-01", tags="quiet")
    kb.state(kb.load()[0], [], limit=1)
    out = capsys.readouterr().out
    assert "    ! 12 " in out
    assert " 10 " not in out and " 11 " not in out


@pytest.mark.parametrize("place", ["analyzed", "noted"])
@pytest.mark.parametrize("first, second", [("release", "quiet"), ("needs-human", "release")])
def test_the_marks_rank_quiet_then_release_then_a_person(kb, capsys, place, first, second):
    """Nothing new is meant to land while a quiet entry is open, so one caught
    after a release entry still comes before it."""
    write(kb, place, "10", kind="work", criterion="c", noted="2026-08-01", tags=first)
    write(kb, place, "11", kind="work", criterion="c", noted="2026-08-02", tags=second)
    kb.state(kb.load()[0], [], limit=1)
    out = capsys.readouterr().out
    assert " 11 " in out and " 10 " not in out


def test_the_marks_are_explained_where_they_first_appear(kb, capsys):
    """A record with nothing ready to pick up still shows marks among what is
    caught, and a mark nobody explains is a character on the line."""
    write(kb, "analyzed", "10", kind="work", criterion="c")
    write(kb, "noted", "11", noted="2026-08-01", tags="release")
    write(kb, "noted", "12", noted="2026-08-02", tags="quiet")
    kb.state(kb.load()[0], [])
    out = capsys.readouterr().out
    assert out.count("! can be wrong quietly") == 1
    assert "caught, not yet shaped (2)   * release" in out


def test_an_identity_is_never_reused(kb):
    write(kb, "done", "1A", kind="work", criterion="c", closed="2026-08-23",
          outcome="judged: done")
    kb.note(["something new"])
    assert {e.id for e in kb.load()[0]} == {"1A", "1B"}


def test_note_adds_to_what_is_already_caught_rather_than_replacing_it(kb):
    kb.note(["the first thing"])
    first = kb.load()[0][0].id
    kb.note([first, "and the second"])
    body = kb.load()[0][0].body
    assert "the first thing" in body and "the second" in body


# --------------------------------------------------------------- the record

def test_the_record_is_found_from_anywhere_inside_the_project(kb, tmp_path, monkeypatch):
    """A command works from a subdirectory the way a version-control command
    does, and the record is recognised by its `project.md`, not by its name."""
    (kb.ROOT / kb.PROJECT).write_text("---\nowned: src\n---\n")
    deep = tmp_path / "src" / "pkg"
    deep.mkdir(parents=True)
    monkeypatch.chdir(deep)
    monkeypatch.delenv("KB_RECORD", raising=False)
    assert kb._record() == kb.ROOT
    monkeypatch.chdir(kb.ROOT / "noted")
    assert kb._record() == kb.ROOT


def test_a_directory_called_kb_with_no_project_file_is_not_a_record(kb, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("KB_RECORD", raising=False)
    with pytest.raises(SystemExit, match="no record here"):
        kb._record()


def test_what_the_record_says_about_itself_shapes_the_tool(kb):
    """Every project-shaped constant comes from `project.md`, so one copy of
    the tool serves two records; the record's own directory is always owned
    and always a citer, since an entry cites its neighbours."""
    (kb.ROOT / kb.PROJECT).write_text(
        "---\nowned: src, vendor\noutside: vendor\nciters: NOTES.md\n"
        "documents: NOTES.md\ntheirs: vendor\nfigure: \\d+ apples\n---\n\nprose about the project\n")
    kb.configure(kb.ROOT, kb._project(kb.ROOT))
    assert kb.OWNED == ("src", "vendor", "kb") and kb.OUTSIDE == ("vendor",)
    assert kb.CITERS == ("kb", "NOTES.md") and kb.DOCUMENTS == ("NOTES.md",)
    assert kb.THEIRS == ("vendor",) and kb.FIGURE.search("3 apples")
    assert kb.PATH.search("see src/a.py::f") and not kb.PATH.search("see app/a.py::f")


def test_a_project_file_that_does_not_parse_stops_the_command(kb):
    (kb.ROOT / kb.PROJECT).write_text("---\nowned: src\n  stray\n")
    with pytest.raises(SystemExit, match="never closed"):
        kb._project(kb.ROOT)


# ------------------------------------------------------------------ counting

def test_an_identity_round_trips_through_its_number(kb):
    for value in (kb.FIRST, kb.FIRST + 1, 1023, 1024, 33000):
        assert kb._number(kb._identity(value)) == value


def test_a_new_identity_is_two_characters_carrying_both_a_digit_and_a_letter(kb):
    kb.note(["the first thing this record ever caught"])
    assert [e.id for e in kb.load()[0]] == ["1A"]


def test_an_all_letter_stretch_of_the_count_is_skipped(kb):
    write(kb, "done", "EQ", kind="work", criterion="c", closed="2026-08-23",
          outcome="judged: done")
    kb.note(["past an all-letter stretch of the count"])
    assert "F0" in {e.id for e in kb.load()[0]}


def test_and_an_all_digit_stretch_is_skipped_too(kb):
    write(kb, "done", "ZZZ", kind="work", criterion="c", closed="2026-08-23",
          outcome="judged: done")
    kb.note(["past the widest three-character identity"])
    assert "100A" in {e.id for e in kb.load()[0]}


# -------------------------------------------------------------------- search

def test_a_search_reaches_every_field_and_not_only_the_prose(kb):
    write(kb, "analyzed", "10", kind="work", criterion="the buffer drains before the shutdown")
    hits = kb._rank(kb.load()[0], kb.words("buffer"))
    assert [e.id for _, e in hits] == ["10"]


def test_a_number_is_a_search_term_like_any_other(kb):
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x",
          body="a 100 ms timeout, p99 measured")
    assert [e.id for _, e in kb._rank(kb.load()[0], kb.words("p99"))] == ["10"]


def test_settled_knowledge_outranks_an_unshaped_note_on_a_tie(kb):
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x", body="buffer")
    write(kb, "noted", "11", body="buffer")
    assert [e.id for _, e in kb._rank(kb.load()[0], kb.words("buffer"))][0] == "10"


def test_breadth_is_not_an_answer_and_the_shorter_of_two_equals_wins(kb):
    """A long entry answers a share of every question, having said everything.

    Both entries below hold the whole question and neither says more about it,
    so without a length penalty they tie and the identity settles it - which is
    the order written here, so a penalty that stopped working would leave this
    green.
    """
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x",
          body="the buffer is reserved over a window " + " ".join(f"w{n}" for n in range(400)))
    write(kb, "known/lib", "11", kind="fact", provenance="judged: x",
          body="the buffer is reserved over a window")
    order = [e.id for _, e in kb._rank(kb.load()[0], kb.words("buffer reserved window"))]
    assert order[0] == "11", f"the long entry outranked the short one: {order}"


def test_a_shaped_entry_is_not_held_back_for_carrying_its_fields(kb):
    """The penalty measures the body, not everything the search reads.

    A criterion and a provenance are what shaping adds, and an entry that ranks
    lower for having them would be a record that rewards leaving them off.
    """
    write(kb, "known/lib", "10", kind="fact", provenance="judged: measured all day",
          body="buffer")
    write(kb, "noted", "11", body="buffer")
    assert [e.id for _, e in kb._rank(kb.load()[0], kb.words("buffer"))][0] == "10"


def test_what_somebody_else_s_software_does_is_offered_one_link_further(kb, capsys):
    """The working set is one link; a measured behaviour two links out, reached
    through a neighbour, is the entry nobody thought to link - and only the
    subjects about software we do not control are worth the second hop."""
    write(kb, "analyzed", "10", kind="work", criterion="c", related="11")
    write(kb, "known/ours", "11", kind="fact", provenance="judged: x", related="12, 13")
    write(kb, "known/client", "12", kind="fact", provenance="judged: a client",
          title="A client renders the last part it is sent")
    write(kb, "known/ours", "13", kind="fact", provenance="judged: ours")
    kb.find(["--near", "10"])
    said = capsys.readouterr().out
    assert "one link past" in said and "renders the last" in said
    assert "13 " not in said.split("one link past")[1]


def test_an_option_nobody_defined_stops_the_search_rather_than_being_eaten(kb):
    with pytest.raises(SystemExit):
        kb.find(["--tagg", "network", "launch"])


def test_a_column_of_titles_is_not_a_column_of_blanks(kb, capsys):
    # `title` is the entry rather than a field of it, and asking for that
    # column came back empty.
    write(kb, "analyzed", "10", kind="work", criterion="c")
    kb.find(["--fields", "title,kind"])
    assert "title: a title" in capsys.readouterr().out


# --------------------------------------------------------------- what re-runs

def _command(kb, name="run-pytest", probe=0, code=0, said="1 passed"):
    """A command under the record's `run/` that keeps the contract: it writes
    each argv and the directory it ran in to a log, and exits `code` saying
    `said`, or `probe` to `--probe`. The trees the citations name are checked
    out, since `stale` passes over one that is not."""
    for tree in ("app", "lib"):
        (kb.REPO / tree).mkdir(exist_ok=True)
    log = kb.ROOT / "run" / f"{name}.log"
    command = kb.ROOT / "run" / name
    command.parent.mkdir(exist_ok=True)
    command.write_text(
        "#!/bin/sh\n"
        f'echo "$PWD $*" >> "{log}"\n'
        f'if [ "$1" = --probe ]; then echo "the toolchain"; exit {probe}; fi\n'
        f'echo "{said}"\nexit {code}\n')
    command.chmod(0o755)
    return log


def _ran(log):
    return [line.split(" ", 1) for line in log.read_text().splitlines()] if log.exists() else []


def _one_test_entry(kb, at="app/tests/test_t.py", name="test_here", identity="10"):
    write(kb, "known/lib", identity, kind="fact",
          provenance=f"test: {at}::{name}" if name else f"test: {at}")


def test_a_citation_is_handed_to_the_records_command_from_the_project_root(kb):
    """How a test is run is the project's, so the tool hands on the citation as
    it stands - the path from the project root and the name after `::` - and
    reads nothing into either."""
    _one_test_entry(kb, name="TestField::test_here")
    log = _command(kb)
    assert kb.stale(kb.load()[0]) == 0
    assert _ran(log) == [[str(kb.REPO), "--probe"],
                         [str(kb.REPO), "app/tests/test_t.py TestField::test_here"]]


def test_a_citation_naming_no_test_hands_on_the_path_alone(kb):
    _one_test_entry(kb, name="")
    log = _command(kb)
    assert kb.stale(kb.load()[0]) == 0
    assert _ran(log)[-1] == [str(kb.REPO), "app/tests/test_t.py"]


def test_a_go_citation_goes_to_the_go_command_and_not_to_pytest(kb):
    """Nothing in a citation says which command owns it but the suffix."""
    _one_test_entry(kb, at="lib/header_test.go", name="TestUnfold")
    python, go = _command(kb), _command(kb, "run-go-test", said="TestUnfold passed")
    assert kb.stale(kb.load()[0]) == 0
    assert _ran(python) == []
    assert _ran(go)[-1] == [str(kb.REPO), "lib/header_test.go TestUnfold"]


@pytest.mark.parametrize("code, verdict", [(0, "green"), (77, "UNRUN"), (1, "RED"), (2, "RED")])
def test_the_verdict_is_the_commands_exit_status(kb, capsys, code, verdict):
    """A skip is the absence of evidence and must not print like the presence of
    it, so the contract gives it a status of its own; anything but the two known
    ones is red."""
    _one_test_entry(kb)
    _command(kb, code=code, said="what became of it")
    status = kb.stale(kb.load()[0])
    printed = capsys.readouterr().out
    if verdict == "green":
        assert status == 0 and "RED" not in printed and "UNRUN" not in printed
    else:
        assert f"{verdict} " in printed and "what became of it" in printed
        assert status == (1 if verdict == "RED" else 0)
        assert ("1 were not run" in printed) == (verdict == "UNRUN")


def test_the_toolchain_is_asked_for_once_and_not_once_per_test(kb):
    _one_test_entry(kb)
    _one_test_entry(kb, name="test_there", identity="11")
    log = _command(kb)
    assert kb.stale(kb.load()[0]) == 0
    assert [argv for _, argv in _ran(log)].count("--probe") == 1


def test_a_record_with_no_command_says_so_once_and_runs_nothing(kb, capsys):
    """A page of the same complaint would bury the one line of real staleness
    the run was for, and a record it could not check is not one it found clean."""
    (kb.REPO / "app").mkdir()
    _one_test_entry(kb)
    _one_test_entry(kb, name="test_there", identity="11")
    assert kb.stale(kb.load()[0]) == 1
    printed = capsys.readouterr().out
    assert printed.count("the record has no executable run/run-pytest") == 1
    assert "2 cited tests" in printed and "2 were not run" in printed
    assert "RED" not in printed


def test_a_command_that_cannot_be_executed_is_no_command(kb, capsys):
    _one_test_entry(kb)
    _command(kb)
    (kb.ROOT / "run" / "run-pytest").chmod(0o644)
    assert kb.stale(kb.load()[0]) == 1
    assert "no executable run/run-pytest" in capsys.readouterr().out


def test_a_probe_saying_the_toolchain_is_not_there_is_said_once_with_its_reason(kb, capsys):
    _one_test_entry(kb)
    _one_test_entry(kb, name="test_there", identity="11")
    log = _command(kb, probe=1)
    assert kb.stale(kb.load()[0]) == 1
    printed = capsys.readouterr().out
    assert printed.count("run/run-pytest --probe: the toolchain") == 1
    assert "2 were not run" in printed and "RED" not in printed
    assert [argv for _, argv in _ran(log)] == ["--probe"]


def test_a_command_nobody_needed_is_never_asked(kb):
    """A record citing only Go must not fail for want of pytest, nor the other
    way about."""
    _one_test_entry(kb, at="lib/header_test.go", name="TestUnfold")
    python = _command(kb, probe=1)
    _command(kb, "run-go-test")
    assert kb.stale(kb.load()[0]) == 0
    assert _ran(python) == []


@pytest.mark.parametrize("at", ["app/tests/test_t.py", "app/tests/t_test.py", "lib/tree_test.go"])
def test_a_file_named_as_a_test_goes_to_its_command(kb, at):
    _one_test_entry(kb, at=at, name="")
    python, go = _command(kb), _command(kb, "run-go-test")
    assert kb.stale(kb.load()[0]) == 0
    ran = _ran(go if at.endswith(".go") else python)
    assert ran[-1] == [str(kb.REPO), at]


@pytest.mark.parametrize("at", ["app/results/run.out", "app/corpus", "app/pyproject.toml",
                                "app/src/lib.rs", "app/src/placed.py", "app/tests/drawings.py",
                                "lib/tree.go", "app/tests/testing_t.py"])
def test_a_path_whose_name_is_no_tests_is_a_mention_and_fails_nothing(kb, capsys, at):
    """A sentence about a test names the code it covers and the helper it drives,
    and `check` holds those names already. Handed to a command they would say
    red, and a red about the citation reads as one about the code."""
    _one_test_entry(kb, at=at, name="")
    python, go = _command(kb), _command(kb, "run-go-test")
    assert kb.stale(kb.load()[0]) == 0
    printed = capsys.readouterr().out
    assert _ran(python) == [] and _ran(go) == []
    assert "1 mentioned beside a test" in printed and "RED" not in printed
    assert "UNKNOWN" not in printed


@pytest.mark.parametrize("at", ["app/tests/test_t.py:82", "app/tests/test_t.py:82-90"])
def test_a_test_file_cited_by_a_line_is_unknown_and_fails(kb, capsys, at):
    """It names a test and addresses none, so the record is unchecked there."""
    _one_test_entry(kb, at=at, name="")
    python = _command(kb)
    assert kb.stale(kb.load()[0]) == 1
    printed = capsys.readouterr().out
    assert _ran(python) == []
    assert "UNKNOWN 10 " in printed and "cite it by its name after ::" in printed


def test_code_cited_by_a_line_beside_a_test_is_still_a_mention(kb, capsys):
    _one_test_entry(kb, at="app/src/placed.py:82", name="")
    _command(kb)
    assert kb.stale(kb.load()[0]) == 0
    assert "1 mentioned beside a test" in capsys.readouterr().out


def test_a_mention_beside_a_test_does_not_keep_the_test_from_running(kb, capsys):
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: app/tests/test_t.py::test_here drives app/tests/probe.py")
    log = _command(kb)
    assert kb.stale(kb.load()[0]) == 0
    assert [argv for _, argv in _ran(log)] == ["--probe", "app/tests/test_t.py test_here"]


def test_the_dry_run_lists_a_mention_and_an_unknown_apart(kb, capsys):
    for tree in ("app", "lib"):
        (kb.REPO / tree).mkdir()
    _one_test_entry(kb)
    _one_test_entry(kb, at="app/src/placed.py", name="placed", identity="11")
    _one_test_entry(kb, at="app/tests/test_t.py:82", name="", identity="12")
    assert kb.dry(kb.load()[0]) == 0
    printed = capsys.readouterr().out
    assert re.search(r"mentioned\s+11\s+-\s+app/src/placed\.py::placed", printed)
    assert re.search(r"no command\s+12\s+-\s+app/tests/test_t\.py:82", printed)
    assert ("1 would be run; 1 cited under test: are no test a command here runs; "
            "1 under test: are mentioned") in printed


def test_one_test_outrunning_the_clock_does_not_stop_the_rest(kb, monkeypatch, capsys):
    _one_test_entry(kb)
    _one_test_entry(kb, name="test_there", identity="11")
    _command(kb)
    real = kb.subprocess.run
    def slow(argv, **kwargs):
        if argv[1] == "--probe":
            return real(argv, **kwargs)
        raise subprocess.TimeoutExpired(argv, 600)
    monkeypatch.setattr(kb.subprocess, "run", slow)
    assert kb.stale(kb.load()[0]) == 1
    assert capsys.readouterr().out.count("did not finish inside the timeout") == 2


def test_only_the_paths_under_test_in_a_field_carrying_several_kinds_are_run(kb, capsys):
    """A fact rests on the tests that hold it and on the measurement that found
    it; the measurement's files are evidence of another kind, and handing them
    to a test runner reports the citation as unchecked."""
    write(kb, "known/lib", "10", kind="fact",
          provenance="test: app/tests/test_t.py::test_here, app/tests/test_u.py; "
                     "measured: app/results/run.out and app/corpus; gate: app/tests/g.py")
    log = _command(kb)
    assert kb.stale(kb.load()[0]) == 0
    assert [argv for _, argv in _ran(log)] == [
        "--probe", "app/tests/test_t.py test_here", "app/tests/test_u.py"]
    assert "no command" not in capsys.readouterr().out
    assert kb.dry(kb.load()[0]) == 0
    printed = capsys.readouterr().out
    assert "app/results" not in printed and "app/tests/g.py" not in printed


@pytest.mark.parametrize("joined", [". test:", " and test:", " (test:", "\ntest:", "; test:"])
def test_a_kinds_word_starting_a_word_starts_its_part_however_it_is_joined(kb, joined):
    """A record writes the boundary a sentence's way as often as a semicolon's,
    and a test cited after `. test:` inside a measurement is a test."""
    carried = kb._evidence(f"measured: the runs are app/results/{joined} app/tests/test_t.py")
    assert [kind for kind, _ in carried] == ["measured", "test"]


def test_a_kinds_word_inside_a_path_or_a_word_starts_nothing(kb):
    assert [k for k, _ in kb._evidence("test: app/tests/test_t.py::attest: x, app/gate:y")] == ["test"]


def test_a_semicolon_inside_one_kind_does_not_start_another(kb):
    assert kb._evidence("measured: a; b and c; judged: d") == [
        ("measured", "measured: a; b and c"), ("judged", "judged: d")]


def test_the_runners_are_the_records_and_route_by_the_files_name(kb):
    """Which files are tests and what runs them is the project's to say."""
    kb.configure(kb.ROOT, {"owned": "app", "runners": "*.test run-program"})
    _one_test_entry(kb, at="app/checks/sum.test", name="")
    _one_test_entry(kb, at="app/tests/test_t.py", identity="11")
    program, python = _command(kb, "run-program"), _command(kb)
    assert kb.stale(kb.load()[0]) == 0
    assert _ran(program)[-1] == [str(kb.REPO), "app/checks/sum.test"]
    assert _ran(python) == []


def test_a_record_naming_no_runner_runs_nothing_and_says_so_once(kb, capsys):
    """A run that ran nothing is not a record found clean."""
    kb.configure(kb.ROOT, {"owned": "app"})
    _one_test_entry(kb)
    _one_test_entry(kb, name="test_there", identity="11")
    log = _command(kb)
    assert kb.stale(kb.load()[0]) == 1
    printed = capsys.readouterr().out
    assert _ran(log) == []
    assert printed.count("names no runners") == 1 and "2 were not run" in printed
    assert kb.dry(kb.load()[0]) == 0
    printed = capsys.readouterr().out
    assert "names no runners" in printed and "mentioned   10" not in printed
    assert "0 would be run; 2 cited under test: are no test a command here runs" in printed


@pytest.mark.parametrize("runners", ["test_*.py", "test_*.py run tests", "*.py ../run-it"])
def test_a_runner_that_is_not_a_pattern_and_a_command_is_refused(kb, runners):
    with pytest.raises(SystemExit) as refused:
        kb.configure(kb.ROOT, {"runners": runners})
    assert "runners:" in str(refused.value)


def test_the_dry_run_names_the_command_each_citation_would_go_to(kb, capsys):
    for tree in ("app", "lib"):
        (kb.REPO / tree).mkdir()
    _one_test_entry(kb)
    _one_test_entry(kb, at="lib/header_test.go", name="TestUnfold", identity="11")
    assert kb.dry(kb.load()[0]) == 0
    printed = capsys.readouterr().out
    assert "run/run-pytest" in printed and "run/run-go-test" in printed


def test_a_question_the_record_cannot_answer_scores_low_rather_than_vanishing(kb):
    # A lone common word matched loudly while the rest of the question went
    # unanswered, so a silent record read exactly like a badly searched one.
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x",
          body="the buffer is reserved over a window")
    hits = kb._rank(kb.load()[0], kb.words("buffer calibration handshake quorum"))
    assert hits and hits[0][0] < kb.THIN


def test_but_a_question_it_does_answer_clears_the_floor(kb):
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x",
          body="the buffer is reserved over a window")
    hits = kb._rank(kb.load()[0], kb.words("buffer reserved window"))
    assert hits[0][0] >= kb.THIN


def test_a_dry_run_names_what_rests_on_prose_without_running_anything(kb, monkeypatch, capsys):
    def never(*a, **k):
        raise AssertionError("a dry run may not start a test")
    monkeypatch.setattr(kb.subprocess, "run", never)
    write(kb, "known/lib", "10", kind="fact", provenance="judged: two runs, gone")
    assert kb.dry(kb.load()[0]) == 0
    assert "no citation" in capsys.readouterr().out


def test_every_guideline_is_printed_by_one_command(kb, capsys):
    # A rule that has to be looked up does not fire, so the whole set is one
    # command cheap enough to run before knowing which of them will bite.
    (kb.ROOT / "known" / kb.GUIDELINES).mkdir(parents=True)
    write(kb, f"known/{kb.GUIDELINES}", "10", kind="fact", provenance="judged: a session")
    write(kb, "known/lib", "11", kind="fact", provenance="judged: x")
    assert kb.rules(kb.load()[0]) == 0
    printed = capsys.readouterr().out
    assert "10" in printed and "11" not in printed.split("\n\n")[0]


def test_a_thin_answer_is_reported_and_not_hidden(kb, capsys):
    # Dropping an entry for sharing few words with the question loses it
    # silently, which is worse than saying the best of them is thin.
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x",
          body="the buffer is reserved over a window")
    kb.find(["buffer", "calibration", "handshake", "quorum"])
    printed = capsys.readouterr().out
    assert "1 found" in printed and "silent on it" in printed


def test_but_a_caller_may_ask_for_the_cut(kb, capsys):
    write(kb, "known/lib", "10", kind="fact", provenance="judged: x",
          body="the buffer is reserved over a window")
    kb.find(["buffer", "calibration", "handshake", "quorum", "--floor", "0.35"])
    assert "nothing here" in capsys.readouterr().out


def test_a_reader_hanging_up_is_not_a_traceback(kb):
    # `find | head` is the normal way to read a long answer, and `head` hangs
    # up as soon as it has its lines. A filter dies quietly on that; the
    # traceback this pins down arrives at interpreter exit, when the final
    # flush meets the closed pipe after main() has already returned cleanly.
    process = subprocess.Popen(
        [sys.executable, str(HERE / "kb.py"), "find", "the"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "KB_RECORD": str(kb.ROOT)},
    )
    process.stdout.close()
    process.wait()
    leaked = process.stderr.read()
    process.stderr.close()
    assert b"BrokenPipeError" not in leaked and b"Traceback" not in leaked


def test_a_draft_s_title_is_folded_in_a_listing_and_whole_when_it_is_read(kb, capsys, monkeypatch):
    # A note costs no decisions to write, so a draft's title is routinely a
    # paragraph. Left whole in a listing it takes six lines and hides the
    # entries under it; the listing is scanned rather than read, so it folds.
    monkeypatch.setenv("COLUMNS", "100")
    long = "A gate line drops its verb " * 12
    path = kb.ROOT / "noted" / "10-slug.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nid: 10\ntitle: {long}\n---\n\nprose\n")

    kb.find(["verb"])
    folded = capsys.readouterr().out
    assert "…" in folded
    assert long not in folded

    # And whole wherever it is read rather than scanned.
    kb.find(["--near", "10"])
    assert long in capsys.readouterr().out


def test_what_a_note_turns_up_carries_its_score_and_folds_like_any_listing(kb, capsys, monkeypatch):
    # Nothing was asked for here, so the reader has to judge each hit rather
    # than trust the order. Without the number they cannot: an entry using all
    # the words and an entry on the subject look the same in a list.
    monkeypatch.setenv("COLUMNS", "100")
    long = "A gate line drops its verb " * 12
    for identity, title in (("10", long), ("11", "Something else entirely")):
        path = kb.ROOT / "noted" / f"{identity}-slug.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nid: {identity}\ntitle: {title}\n---\n\nprose\n")

    kb.note(["a gate line drops its verb"])
    turned_up = capsys.readouterr().out
    assert "already recorded:" in turned_up
    assert re.search(r"\d+%\s+10\b", turned_up), turned_up

    # And a paragraph of a title folds here as it does anywhere it is scanned.
    assert "…" in turned_up and long not in turned_up


# ------------------------------------------------------------ writing a field

def _text(kb, place, identity):
    return next((kb.ROOT / place).glob(f"{identity}-*.md")).read_text()


def _source(kb, cited):
    """The file and the test a citation names, so `check` finds them there."""
    page, _, name = cited.partition("::")
    (kb.REPO / page).parent.mkdir(parents=True, exist_ok=True)
    (kb.REPO / page).write_text(f"def {name}():\n    pass\n")


def test_set_writes_one_field_and_leaves_every_other_line_as_it_was(kb):
    write(kb, "scoped", "10", kind="work", criterion="old", tags="kb", body="the prose")
    before = _text(kb, "scoped", "10")
    kb.set_field(["10", "criterion", "new"])
    after = _text(kb, "scoped", "10")
    assert after == before.replace("criterion: old", "criterion: new")


def test_a_field_carried_on_indented_lines_is_replaced_whole(kb):
    """A replace that took only the first line of a carried field would leave
    its tail joined onto whatever field it now sits under."""
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_text("---\nid: 10\ntitle: t\nkind: work\ncriterion: one\n    two\n"
                    "tags: kb\n---\n\nprose\n")
    kb.set_field(["10", "criterion", "three"])
    (entry,), _ = kb.load()
    assert entry.fields == {"kind": "work", "criterion": "three", "tags": "kb"}


def test_a_field_the_entry_lacks_is_added_to_its_head(kb):
    write(kb, "scoped", "10", kind="work", criterion="c", body="the prose")
    kb.set_field(["10", "outcome", "judged:", "it", "holds"])
    (entry,), _ = kb.load()
    assert entry.fields["outcome"] == "judged: it holds"
    assert entry.body.strip() == "the prose"


def test_a_long_value_is_carried_at_spaces_and_reads_back_as_written(kb):
    """A citation broken at its hyphen or after its colons is one nothing reads."""
    cited = "app/tests/test_some_long-named_file.py::test_a_long_name"
    _source(kb, cited)
    value = " ".join(["words"] * 30 + [cited] + ["more"] * 10)
    write(kb, "scoped", "10", kind="work", criterion="c")
    kb.set_field(["10", "outcome", value])
    text = _text(kb, "scoped", "10")
    assert max(len(line) for line in text.split("\n") if cited not in line) <= kb.WIDTH
    assert any(line.strip() == cited or cited in line.split() for line in text.split("\n"))
    (entry,), _ = kb.load()
    assert entry.fields["outcome"] == value


def test_set_will_not_write_an_identity_or_a_field_the_format_lacks(kb):
    write(kb, "scoped", "10", kind="work", criterion="c")
    before = _text(kb, "scoped", "10")
    for name in ("id", "critereon"):
        with pytest.raises(SystemExit, match="not a field set can write"):
            kb.set_field(["10", name, "x"])
    assert _text(kb, "scoped", "10") == before


def test_a_write_that_would_read_back_differently_writes_nothing(kb, monkeypatch):
    """The fault this answers: a replace in the head lost its closing fence,
    and only the next `check` noticed."""
    write(kb, "scoped", "10", kind="work", criterion="c")
    before = _text(kb, "scoped", "10")
    monkeypatch.setattr(kb, "_head_line", lambda name, value: f"{name}: {value}\n---")
    with pytest.raises(SystemExit, match="nothing written"):
        kb.set_field(["10", "criterion", "new"])
    assert _text(kb, "scoped", "10") == before


@pytest.mark.parametrize("line", ["{name}: {value}\ntags: smuggled",
                                  "{name}: {value}\nneither field nor prose",
                                  "{name}: {value}\n---"])
def test_and_neither_does_one_that_would_move_another_field_or_the_form(kb, monkeypatch, line):
    write(kb, "scoped", "10", kind="work", criterion="c", tags="kb")
    before = _text(kb, "scoped", "10")
    monkeypatch.setattr(kb, "_head_line", lambda name, value: line.format(name=name, value=value))
    with pytest.raises(SystemExit, match="nothing written"):
        kb.set_field(["10", "criterion", "new"])
    assert _text(kb, "scoped", "10") == before


def test_a_title_is_written_on_one_line_however_long(kb):
    write(kb, "noted", "10")
    title = "a caught thought " * 20
    kb.set_field(["10", "title", title])
    assert f"\ntitle: {title.strip()}\n" in _text(kb, "noted", "10")


def test_a_carried_line_that_opens_like_the_field_is_not_the_field(kb):
    """A paragraph wrapped under one field may begin a line with another's name."""
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_text("---\nid: 10\ntitle: t\nkind: work\ncriterion: the\n"
                    "    outcome: of it\n---\n\nprose\n")
    kb.set_field(["10", "outcome", "judged: holds"])
    (entry,), _ = kb.load()
    assert entry.fields["criterion"] == "the outcome: of it"
    assert entry.fields["outcome"] == "judged: holds"


def test_a_file_that_changed_under_the_writer_is_not_written(kb):
    write(kb, "scoped", "10", kind="work", criterion="c")
    (entry,), _ = kb.load()
    with pytest.raises(SystemExit, match="changed since it was read"):
        kb._with(entry, "---\nid: 10\n", "criterion", "new")


def test_a_file_whose_head_is_already_broken_is_left_to_a_hand(kb):
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_text("---\nid: 10\ntitle: t\nkind: work\n")
    with pytest.raises(SystemExit):
        kb.set_field(["10", "criterion", "c"])
    assert path.read_text() == "---\nid: 10\ntitle: t\nkind: work\n"


# ------------------------------------------------------------------ closing

def test_close_dates_the_entry_and_moves_it(kb):
    write(kb, "scoped", "10", kind="work", criterion="c", outcome="judged: it holds")
    kb.close(["10"])
    (entry,), broken = kb.load()
    assert entry.place == "done" and broken == []
    assert entry.fields["closed"] == kb.date.today().isoformat()
    assert kb.check([entry], []) == []


def test_a_closure_the_place_would_refuse_stays_where_it_was(kb):
    write(kb, "scoped", "10", kind="work", criterion="c")
    write(kb, "scoped", "11", kind="work", criterion="c", outcome="a summary")
    for identity in ("10", "11"):
        before = _text(kb, "scoped", identity)
        with pytest.raises(SystemExit, match=f"{identity} stays in scoped"):
            kb.close([identity])
        assert _text(kb, "scoped", identity) == before
    assert not list((kb.ROOT / "done").iterdir())


def test_a_road_put_down_is_held_to_its_reason(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c")
    with pytest.raises(SystemExit, match="moot with no because"):
        kb.close(["10", "moot"])
    kb.set_field(["10", "because", "superseded by 11"])
    kb.close(["10", "moot"])
    (entry,), _ = kb.load()
    assert entry.place == "moot"


def test_a_closure_still_marked_quiet_is_refused(kb):
    write(kb, "scoped", "10", kind="work", criterion="c", outcome="judged: ok", tags="quiet")
    with pytest.raises(SystemExit, match="quiet on a done entry"):
        kb.close(["10"])


def test_a_date_already_written_is_kept(kb):
    write(kb, "scoped", "10", kind="work", criterion="c", outcome="judged: ok",
          closed="2026-08-01")
    kb.close(["10"])
    (entry,), _ = kb.load()
    assert entry.fields["closed"] == "2026-08-01"


def test_close_will_not_move_a_finished_entry_or_onto_another_file(kb):
    write(kb, "done", "10", kind="work", criterion="c", outcome="judged: ok",
          closed="2026-08-01")
    with pytest.raises(SystemExit, match="already done"):
        kb.close(["10", "refused"])
    # A file of that name already in the place, whatever it holds, is not
    # written over: a rename replaces its target without a word.
    write(kb, "scoped", "11", kind="work", criterion="c", outcome="judged: ok")
    squatter = kb.ROOT / "done" / "11-slug.md"
    squatter.write_text("---\nid: 12\ntitle: t\n---\n\nprose\n")
    with pytest.raises(SystemExit, match="is there already"):
        kb.close(["11"])
    assert "id: 12" in squatter.read_text()
    with pytest.raises(SystemExit, match="not a place"):
        kb.close(["10", "analyzed"])


# ------------------------------------------------------- grown past its body

def _noted(count):
    return "the body\n" + "".join(f"\n*2026-09-12* - note {n}\n" for n in range(count))


def test_a_shaped_entry_grown_by_notes_past_its_body_is_listed(kb):
    """Two notes are what a closure ordinarily takes after it - the adversarial
    tester's finding and the review - and a third is the body overtaken."""
    write(kb, "done", "10", kind="work", criterion="c", outcome="judged: ok",
          closed="2026-09-12", body=_noted(3))
    write(kb, "done", "11", kind="work", criterion="c", outcome="judged: ok",
          closed="2026-09-12", body=_noted(2))
    assert [(n, e.id) for n, e in kb.grown(kb.load()[0])] == [(3, "10")]


def test_but_a_caught_thought_may_be_a_mess(kb):
    write(kb, "noted", "10", body=_noted(kb.GROWN + 5))
    assert kb.grown(kb.load()[0]) == []


def test_a_date_inside_prose_is_not_a_note(kb):
    body = "the body\n" + "measured on *2026-09-12* - and again\n" * (kb.GROWN + 1)
    write(kb, "scoped", "10", kind="work", criterion="c", body=body)
    assert kb.grown(kb.load()[0]) == []


def test_grown_is_a_prompt_the_session_sees_and_not_a_fault(kb, capsys, monkeypatch):
    (kb.ROOT / kb.PROJECT).write_text("---\nowned: app\n---\n")
    monkeypatch.setenv("KB_RECORD", str(kb.ROOT))
    write(kb, "scoped", "10", kind="work", criterion="c", body=_noted(kb.GROWN + 1))
    assert kb.main(["kb.py", "check"]) == 0
    said = capsys.readouterr().out
    assert "grown by dated notes" in said and "10" in said and "walkable" not in said
    kb.main(["kb.py"])
    assert "1 grown past their body" in capsys.readouterr().out


def test_a_caught_thought_worked_past_catching_is_listed_as_work_without_a_criterion(kb):
    """Catching a thought and adding to it once or twice is a thought; notes
    past that are work, which nothing in `noted/` promises to finish."""
    write(kb, "noted", "10", body=_noted(kb.GROWN + 1))
    write(kb, "noted", "11", body=_noted(kb.GROWN))
    write(kb, "scoped", "12", kind="work", criterion="c", body=_noted(kb.GROWN + 1))
    assert [(n, e.id) for n, e in kb.worked_unshaped(kb.load()[0])] == [(kb.GROWN + 1, "10")]


def test_work_without_a_criterion_is_a_prompt_the_session_sees(kb, capsys, monkeypatch):
    (kb.ROOT / kb.PROJECT).write_text("---\nowned: app\n---\n")
    monkeypatch.setenv("KB_RECORD", str(kb.ROOT))
    write(kb, "noted", "10", body=_noted(kb.GROWN + 1))
    assert kb.main(["kb.py", "check"]) == 0
    said = capsys.readouterr().out
    assert "worked on while still caught" in said and "10" in said and "walkable" not in said
    kb.main(["kb.py"])
    assert "1 worked on while still caught" in capsys.readouterr().out


# ------------------------------------------------------ a working set, carded

def _set(kb):
    write(kb, "scoped", "10", kind="work", criterion="the task's criterion",
          related="11, 12", body="the task's prose")
    write(kb, "refused", "11", kind="work", criterion="the refused road's criterion",
          because="why it was put down", closed="2026-09-01",
          body="the refused road's prose")
    write(kb, "noted", "14", title="a thought beside it", body="[[10]]")
    write(kb, "done", "12", kind="work", criterion="c", closed="2026-09-01",
          outcome="test: app/tests/test_x.py::test_the_claim_it_holds",
          body="the closed work's prose")
    write(kb, "known/lib", "13", kind="fact", provenance="judged: seen",
          title="what the client does", body="the fact's prose. It bears on [[10]].")


def test_a_neighbour_is_a_card_saying_why_and_what_decides(kb, capsys):
    _set(kb)
    kb.find(["--near", "10"])
    said = capsys.readouterr().out
    assert "the task's criterion" in said and "the task's prose" in said
    assert "because: why it was put down" in said
    assert "the refused road's criterion" not in said
    assert "the refused road's prose" not in said and "the fact's prose" not in said
    assert "what the client does" in said and "> It bears on [[10]]." in said


def test_the_card_says_which_way_the_link_runs(kb, capsys):
    _set(kb)
    kb.find(["--near", "10"])
    said = capsys.readouterr().out
    assert re.search(r"11\s+\[refused\]\s+cited here", said)
    assert re.search(r"13\s+\[lib\]\s+cites this", said)


def test_a_road_put_down_is_read_before_what_was_finished(kb, capsys):
    _set(kb)
    kb.find(["--near", "10"])
    said = capsys.readouterr().out
    assert said.index("put down:") < said.index("open:") < said.index("known:") \
        < said.index("finished:")


def test_a_card_reads_a_citation_by_the_name_it_cites(kb, capsys):
    _set(kb)
    kb.find(["--near", "10"])
    said = capsys.readouterr().out
    assert "outcome: test: test_the_claim_it_holds" in said
    assert "app/tests" not in said


def test_full_prints_every_neighbour_whole(kb, capsys):
    _set(kb)
    kb.find(["--near", "10", "--full"])
    said = capsys.readouterr().out
    assert "the refused road's prose" in said and "the fact's prose" in said


def test_a_working_set_is_not_cut_onto_a_second_page(kb, capsys):
    write(kb, "scoped", "10", kind="work", criterion="c",
          related=", ".join(str(n) for n in range(11, 31)))
    for n in range(11, 31):
        write(kb, "noted", str(n), title=f"neighbour {n}")
    kb.find(["--near", "10"])
    said = capsys.readouterr().out
    assert "neighbour 30" in said and "--page" not in said


# ------------------------------------------- what set and close will not do

def test_set_will_not_blank_a_title_and_drop_the_entry(kb):
    """An entry `load` drops leaves its identity looking free to `note`."""
    write(kb, "scoped", "10", kind="work", criterion="c")
    before = _text(kb, "scoped", "10")
    for blank in ("", "   "):
        with pytest.raises(SystemExit, match="title not written"):
            kb.set_field(["10", "title", blank])
    assert _text(kb, "scoped", "10") == before


def test_set_leaves_a_file_it_cannot_read_exactly_alone(kb):
    path = write(kb, "scoped", "10", kind="work", criterion="c", body="prose \xff")
    path.write_bytes(path.read_bytes().replace("\xff".encode(), b"\xff\xfe"))
    before = path.read_bytes()
    with pytest.raises(SystemExit, match="not UTF-8"):
        kb.set_field(["10", "criterion", "new"])
    assert path.read_bytes() == before


@pytest.mark.parametrize("name,value", [("outcome", "a summary"), ("related", "ZZ9"),
                                        ("working", "nothere.md")])
def test_set_will_not_write_what_the_entrys_place_refuses(kb, name, value):
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-01",
          outcome="judged: holds")
    before = _text(kb, "done", "10")
    with pytest.raises(SystemExit, match=f"{name} not written"):
        kb.set_field(["10", name, value])
    assert _text(kb, "done", "10") == before


def test_but_a_fault_already_there_does_not_stop_mending_another(kb):
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-01",
          outcome="judged: holds", related="ZZ9")
    kb.set_field(["10", "criterion", "mended"])
    assert kb.load()[0][0].fields["criterion"] == "mended"


def test_set_says_what_it_replaced(kb, capsys):
    write(kb, "scoped", "10", kind="work", criterion="the old one")
    kb.set_field(["10", "criterion", "the new one"])
    assert "criterion was: the old one" in capsys.readouterr().out


def test_close_will_not_move_an_entry_whose_form_check_refuses(kb):
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_text("---\nid: 10\ntitle: t\nkind: work\ncriterion: c\noutcome: a\n"
                    "outcome: judged: b\n---\n\nprose\n")
    with pytest.raises(SystemExit, match="written twice"):
        kb.close(["10"])
    assert path.exists()


def test_a_citation_longer_than_a_line_is_carried_whole(kb):
    cited = ("app/tests/test_a_header_folded_across_lines.py::"
             "test_a_header_folded_past_the_line_limit_is_unfolded_whole")
    _source(kb, cited)
    write(kb, "scoped", "10", kind="work", criterion="c")
    kb.set_field(["10", "outcome", f"test: {cited}, and more words after it"])
    assert any(cited in line for line in _text(kb, "scoped", "10").split("\n"))


def test_a_link_both_entries_hold_is_said_both_ways(kb, capsys):
    write(kb, "scoped", "10", kind="work", criterion="c", related="11")
    write(kb, "analyzed", "11", kind="work", criterion="c", related="10")
    kb.find(["--near", "10"])
    assert re.search(r"11\s+\[analyzed\]\s+both ways", capsys.readouterr().out)


def test_a_neighbour_citing_in_its_prose_shows_the_sentence_that_does(kb, capsys):
    write(kb, "scoped", "1A", kind="work", criterion="c")
    write(kb, "noted", "1B", related="1A",
          body="Something unrelated. The probe in 1A reads the wrong side. More.")
    write(kb, "noted", "1C", body="First. Then [[1A]] was measured again. Last.")
    kb.find(["--near", "1A"])
    said = capsys.readouterr().out
    assert "> The probe in 1A reads the wrong side." in said
    assert "> Then [[1A]] was measured again." in said
    assert "Something unrelated" not in said and "side. More" not in said
    assert "again. Last" not in said


def test_a_path_naming_nothing_inside_it_is_left_whole_on_a_card(kb, capsys):
    write(kb, "scoped", "10", kind="work", criterion="c", related="11")
    write(kb, "refused", "11", kind="decision", closed="2026-09-01",
          because="read in spec/protocol.txt:1324")
    kb.find(["--near", "10"])
    assert "spec/protocol.txt:1324" in \
        capsys.readouterr().out


# ---------------------------------- what the adversarial tester refuted

def test_set_will_not_write_a_bracketed_citation_that_leads_nowhere(kb):
    write(kb, "scoped", "10", kind="work", criterion="c")
    with pytest.raises(SystemExit, match=r"\[\[ZZ9\]\] leads nowhere"):
        kb.set_field(["10", "criterion", "fails when [[ZZ9]] does"])


def test_a_second_copy_of_a_fault_is_a_fault_set_adds(kb):
    (kb.REPO / "app").mkdir(parents=True)
    (kb.REPO / "app" / "g.py").write_text("def here(): pass\n")
    cited = "app/g.py::gone"
    write(kb, "scoped", "10", kind="work", criterion="c", body=f"it rests on {cited}")
    with pytest.raises(SystemExit, match="criterion not written"):
        kb.set_field(["10", "criterion", f"test: {cited}"])


def test_close_will_not_move_an_entry_citing_nothing_in_its_prose(kb):
    write(kb, "scoped", "10", kind="work", criterion="c", outcome="judged: done",
          body="See also [[ZZ9]].")
    with pytest.raises(SystemExit, match=r"\[\[ZZ9\]\] leads nowhere"):
        kb.close(["10"])
    assert list((kb.ROOT / "scoped").glob("10-*"))


def test_close_will_not_leave_a_measurement_defending_nothing(kb):
    """A claim in known/status/ put down takes the number its measurements
    defend with it."""
    write(kb, "known/status", "10", kind="fact", provenance="judged: claimed")
    write(kb, "analyzed", "11", kind="work", criterion="c", tags="measurement", related="10")
    kb.set_field(["10", "because", "superseded"])
    with pytest.raises(SystemExit, match="a measurement defending no stated number"):
        kb.close(["10", "moot"])


def test_a_head_holding_a_field_twice_is_left_to_a_hand(kb):
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_text("---\nid: 10\ntitle: t\nkind: work\ncriterion: one\ncriterion: two\n"
                    "---\n\nprose\n")
    before = path.read_text()
    with pytest.raises(SystemExit, match="written twice"):
        kb.set_field(["10", "criterion", "three"])
    assert path.read_text() == before


def test_a_value_that_is_not_utf8_writes_nothing(kb):
    path = write(kb, "scoped", "10", kind="work", criterion="c")
    before = path.read_bytes()
    with pytest.raises(SystemExit, match="not UTF-8"):
        kb.set_field(["10", "criterion", "bad \udcff byte"])
    assert path.read_bytes() == before
    assert not list(path.parent.glob("*.writing"))


def test_a_working_name_no_file_system_can_hold_is_a_fault_and_not_a_crash(kb):
    write(kb, "done", "10", kind="work", criterion="c", closed="2026-09-01",
          outcome="judged: done", working="w" * 400)
    assert any("working names" in fault for fault in faults(kb))


def test_a_citation_of_a_split_entry_is_a_link_to_its_parts(kb, capsys):
    write(kb, "scoped", "1B", kind="work", criterion="c", body="It rests on [[1A]].")
    write(kb, "analyzed", "1A.1", kind="work", criterion="c")
    write(kb, "analyzed", "1A.2", kind="work", criterion="c")
    kb.find(["--near", "1B"])
    said = capsys.readouterr().out
    assert "1A.1" in said and "1A.2" in said
    kb.find(["--near", "1A.1"])
    said = capsys.readouterr().out
    assert re.search(r"1B\s+\[scoped\]\s+cites this", said)
    assert "> It rests on [[1A]]." in said


def test_a_bracketed_citation_in_any_field_is_a_link(kb, capsys):
    write(kb, "scoped", "10", kind="work", criterion="as [[11]] measures it")
    write(kb, "analyzed", "11", kind="work", criterion="c")
    kb.find(["--near", "10"])
    assert re.search(r"11\s+\[analyzed\]\s+cited here", capsys.readouterr().out)


def test_a_long_sentence_is_quoted_about_its_citation(kb, capsys, monkeypatch):
    monkeypatch.setenv("COLUMNS", "100")
    write(kb, "scoped", "1A", kind="work", criterion="c")
    long = " ".join(["words that say nothing"] * 30)
    write(kb, "noted", "1B", related="1A", body=f"{long} and then [[1A]] at the end.")
    kb.find(["--near", "1A"])
    assert "[[1A]] at the end." in capsys.readouterr().out


# ------------------------------------------------ what the clean reader found

def test_a_kind_may_be_written_before_the_field_it_asks_for(kb):
    """The order the fields are set in decides nothing: `kind work` trades the
    fault of having no kind for the one of having no criterion."""
    write(kb, "analyzed", "10")
    write(kb, "analyzed", "11")
    kb.set_field(["10", "kind", "work"])
    kb.set_field(["11", "kind", "decision"])
    assert faults(kb) == ["analyzed/10-slug.md: work with nothing that would show it done",
                          "analyzed/11-slug.md: a decision with no reasoning to fail"]
    kb.set_field(["10", "criterion", "something observable"])
    kb.set_field(["11", "because", "a reason"])
    assert faults(kb) == []


def test_but_a_value_that_is_itself_wrong_is_no_trade(kb):
    write(kb, "analyzed", "10")
    before = _text(kb, "analyzed", "10")
    with pytest.raises(SystemExit, match="kind not written"):
        kb.set_field(["10", "kind", "wurk"])
    assert _text(kb, "analyzed", "10") == before


def test_and_a_field_asked_for_where_nothing_was_mended_is_refused(kb):
    write(kb, "analyzed", "10", kind="work", criterion="c")
    with pytest.raises(SystemExit, match="kind not written"):
        kb.set_field(["10", "kind", "decision"])


def test_a_bare_identity_ending_a_sentence_is_quoted_on_its_card(kb, capsys):
    write(kb, "scoped", "1A", kind="work", criterion="c")
    write(kb, "noted", "1B", related="1A", body="Something unrelated. The probe in 1A. Last one.")
    write(kb, "noted", "1C", related="1A", body="Beside it. It rests on 1A.2 alone. Last.")
    kb.find(["--near", "1A"])
    said = capsys.readouterr().out
    assert "> The probe in 1A." in said
    assert "It rests on" not in said


def test_close_makes_the_terminal_place_a_record_never_had(kb):
    (kb.ROOT / "refused").rmdir()
    write(kb, "scoped", "10", kind="work", criterion="c", because="no longer wanted")
    kb.close(["10", "refused"])
    (entry,), _ = kb.load()
    assert entry.place == "refused"


def test_a_field_that_would_not_read_back_as_written_is_not_written(kb):
    write(kb, "scoped", "10", kind="work", criterion="c")
    (entry,), _ = kb.load()
    text = _text(kb, "scoped", "10")
    with pytest.raises(SystemExit, match="would change more than criterion"):
        kb._with(entry, text, "criterion", "one\ntwo")


def test_a_neighbour_fault_already_there_does_not_hold_a_closure_back(kb):
    write(kb, "scoped", "10", kind="work", criterion="c", outcome="judged: ok", related="11")
    write(kb, "analyzed", "11", kind="work", related="10")
    kb.close(["10"])
    assert {e.id: e.place for e in kb.load()[0]} == {"10": "done", "11": "analyzed"}


def test_a_blank_line_inside_a_carried_field_is_part_of_it(kb):
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_text("---\nid: 10\ntitle: t\nkind: work\ncriterion: one\n    two\n\n"
                    "    three\n\ntags: kb\n---\n\nprose\n")
    kb.set_field(["10", "criterion", "new"])
    (entry,), _ = kb.load()
    assert entry.fields == {"kind": "work", "criterion": "new", "tags": "kb"}
    assert "criterion: new\n\ntags: kb\n" in path.read_text()


def test_adding_to_a_note_leaves_a_byte_it_cannot_read_alone(kb):
    path = write(kb, "noted", "10", body="prose \xff")
    path.write_bytes(path.read_bytes().replace("\xff".encode(), b"\xff\xfe"))
    before = path.read_bytes()
    with pytest.raises(SystemExit, match="not UTF-8"):
        kb.note(["10", "more"])
    assert path.read_bytes() == before


def test_a_page_past_the_last_says_so(kb, capsys):
    write(kb, "scoped", "10", kind="work", criterion="c", related="11")
    write(kb, "noted", "11")
    kb.find(["--near", "10", "--page", "2"])
    said = capsys.readouterr().out
    assert "page 2 is past the last" in said and "showing 3-2" not in said


def test_a_tree_the_project_skips_is_not_searched(kb):
    for folder in ("src", "src/vendor"):
        (kb.REPO / folder).mkdir(parents=True, exist_ok=True)
        (kb.REPO / folder / "page.md").write_text("the folded header unfolds\n")
    kb.configure(kb.ROOT, {"source": "src", "skip": "vendor"})
    assert [where for where, _, _ in kb._in_source({"folded", "header"}, 5)] == ["src/page.md"]


# ------------------------------------------------- what a plausible input broke

def test_note_never_hands_out_an_identity_a_broken_file_is_named_after(kb, capsys):
    """`load` drops a file it cannot read, and its identity is still in use."""
    (kb.ROOT / "analyzed" / "1B-broken.md").write_text("---\nid: 1B\n---\n\nno title\n")
    write(kb, "noted", "1A")
    kb.note(["another thing"])
    assert list((kb.ROOT / "noted").glob("1B-*")) == []
    assert [p.name for p in (kb.ROOT / "noted").glob("*-another-thing.md")] == \
        ["1C-another-thing.md"]


def test_note_makes_the_directory_it_writes_to(kb):
    (kb.ROOT / "noted").rmdir()
    kb.note(["a first thought"])
    assert [p.name for p in (kb.ROOT / "noted").iterdir()] == ["1A-a-first-thought.md"]


def test_a_note_in_another_script_is_found_and_named(kb, capsys):
    kb.note(["кэш протухает после рестарта"])
    assert [p.name for p in (kb.ROOT / "noted").iterdir()] == \
        ["1A-кэш-протухает-после-рестарта.md"]
    capsys.readouterr()
    kb.find(["кэш"])
    printed = capsys.readouterr().out
    assert "1 found" in printed and "100%" in printed
    kb.find(["отказ"])
    assert "1 found" not in capsys.readouterr().out


def test_a_title_of_punctuation_still_names_a_file(kb):
    kb.note(["?!"])
    assert [p.name for p in (kb.ROOT / "noted").iterdir()] == ["1A-note.md"]


def test_a_question_of_stopwords_alone_finds_nothing_rather_than_everything(kb, capsys):
    write(kb, "noted", "10")
    kb.find(["the", "of"])
    assert "nothing here" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [["--limit", "abc"], ["--page", "0"], ["--floor", "x"]])
def test_a_number_that_is_not_one_is_refused_by_name(kb, argv):
    with pytest.raises(SystemExit) as refused:
        kb.find(["x", *argv])
    assert argv[0] in str(refused.value)


def test_stale_passes_over_a_test_in_a_tree_the_working_copy_is_without(kb, capsys):
    """As `check` passes over its citations: an absent tree says nothing."""
    (kb.REPO / "lib").mkdir()
    _one_test_entry(kb, at="app/tests/test_t.py")
    _one_test_entry(kb, at="lib/tests/test_l.py", identity="11")
    log = _command(kb)
    (kb.REPO / "app").rmdir()
    assert kb.stale(kb.load()[0]) == 0
    assert [argv for _, argv in _ran(log)] == ["--probe", "lib/tests/test_l.py test_here"]
    assert "1 in a tree that is not here" in capsys.readouterr().out
    assert kb.dry(kb.load()[0]) == 0
    printed = capsys.readouterr().out
    assert re.search(r"not here\s+10\s+-\s+app/tests/test_t\.py", printed)
    assert "1 would be run" in printed and "1 in a tree that is not here" in printed


def test_a_python_file_this_interpreter_cannot_parse_is_held_to_the_word(kb):
    """It may be written for a newer Python than the one running the tool."""
    (kb.REPO / "app").mkdir()
    (kb.REPO / "app" / "new.py").write_text("def test_here():\n    match ? :\n")
    (kb.REPO / "app" / "nul.py").write_text("def test_nul(): pass\n\x00\n")
    write(kb, "known/lib", "10", kind="fact", provenance="test: app/new.py::test_here")
    write(kb, "known/lib", "11", kind="fact", provenance="test: app/nul.py::test_nul")
    assert faults(kb) == []
    write(kb, "known/lib", "12", kind="fact", provenance="test: app/new.py::test_gone")
    assert any("test_gone" in f for f in faults(kb))


def test_a_file_with_cr_lf_lines_is_refused_rather_than_rewritten(kb):
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_bytes(b"---\r\nid: 10\r\ntitle: t\r\nkind: work\r\ncriterion: c\r\n---\r\n\r\nx\r\n")
    before = path.read_bytes()
    with pytest.raises(SystemExit) as refused:
        kb.set_field(["10", "criterion", "d"])
    assert "CR LF" in str(refused.value) and path.read_bytes() == before


@pytest.mark.parametrize("cited", [
    "https://example.org/other/blob/main/app/lib/thing.c",
    "vendor/app/lib/thing.c", "my-app/lib/thing.c"])
def test_an_owned_trees_name_inside_another_path_is_no_citation(kb, cited):
    (kb.REPO / "app").mkdir()
    write(kb, "known/lib", "10", kind="fact", provenance=f"cited: {cited}")
    assert faults(kb) == []


def test_an_owned_tree_still_opens_a_citation_after_dot_slash(kb):
    (kb.REPO / "app").mkdir()
    write(kb, "known/lib", "10", kind="fact", provenance="source: ./app/gone.py")
    assert any("app/gone.py" in f for f in faults(kb))


def test_a_tree_written_with_a_slash_is_the_tree(kb):
    kb.configure(kb.ROOT, {"owned": "app/, ./lib", "outside": "lib/"})
    assert kb.OWNED[:2] == ("app", "lib") and kb.OUTSIDE == ("lib",)
    (kb.REPO / "app").mkdir()
    write(kb, "known/lib", "10", kind="fact", provenance="source: app/gone.py")
    assert any("app/gone.py" in f for f in faults(kb))


def test_a_head_closed_at_the_very_end_of_the_file_is_closed(kb):
    (kb.ROOT / "project.md").write_text("---\nowned: app\n---")
    assert kb._project(kb.ROOT) == {"owned": "app"}
    path = kb.ROOT / "scoped" / "10-slug.md"
    path.write_text("---\nid: 10\ntitle: t\nkind: work\ncriterion: c\n---")
    assert faults(kb) == []
    kb.set_field(["10", "criterion", "d"])
    assert "criterion: d" in path.read_text() and faults(kb) == []


def test_a_document_that_is_a_directory_is_every_page_in_it(kb):
    (kb.REPO / "app").mkdir()
    (kb.REPO / "app" / "x.py").write_text("def here(): pass\n")
    (kb.REPO / "docs" / "deep").mkdir(parents=True)
    (kb.REPO / "docs" / "deep" / "page.md").write_text("see app/x.py::gone\n")
    kb.configure(kb.ROOT, {"owned": "app", "documents": "docs"})
    assert any("docs/deep/page.md" in f and "gone" in f for f in faults(kb))


def test_a_dangling_link_in_a_searched_tree_is_passed_over(kb):
    (kb.REPO / "src").mkdir()
    (kb.REPO / "src" / "page.md").write_text("the folded header unfolds\n")
    (kb.REPO / "src" / "dead.py").symlink_to(kb.REPO / "src" / "nowhere.py")
    kb.configure(kb.ROOT, {"source": "src"})
    assert [w for w, _, _ in kb._in_source({"folded", "header"}, 5)] == ["src/page.md"]


def test_the_summary_says_every_kind_a_fact_rests_on(kb, capsys):
    write(kb, "known/lib", "10", kind="fact", provenance="measured: a run; judged: b")
    write(kb, "known/lib", "11", kind="fact",
          provenance="measured: a run; test: app/tests/test_t.py::test_here")
    kb.state(kb.load()[0], [])
    printed = capsys.readouterr().out
    assert "rests on measured, judged: 10" in printed
    assert "11 " not in printed.split("rests on", 1)[1]


def test_a_cited_test_reads_nothing_from_what_kb_was_started_with(kb, monkeypatch):
    """A test asking for input would otherwise wait on kb's own stdin until the
    clock ran out."""
    _one_test_entry(kb)
    _command(kb)
    real, given = kb.subprocess.run, []
    def watched(argv, **kwargs):
        given.append(kwargs.get("stdin"))
        return real(argv, **kwargs)
    monkeypatch.setattr(kb.subprocess, "run", watched)
    assert kb.stale(kb.load()[0]) == 0
    assert given == [subprocess.DEVNULL, subprocess.DEVNULL]


def test_a_name_no_path_reaches_is_told_which_trees_a_path_may_start_in(kb):
    write(kb, "known/lib", "10", kind="fact", provenance="test: tests/t.py::test_here")
    assert any("no path reaches" in f and "lists as owned" in f for f in faults(kb))


def test_a_record_short_of_a_command_is_sent_to_its_own_contract(kb, capsys):
    (kb.REPO / "app").mkdir()
    _one_test_entry(kb)
    assert kb.stale(kb.load()[0]) == 1
    assert "no executable run/run-pytest - see kb/run/README.md" in capsys.readouterr().out
    kb.configure(kb.ROOT, {"owned": "app"})
    assert kb.stale(kb.load()[0]) == 1
    assert "names no runners, so no command here runs a test - see kb/run/README.md" \
        in capsys.readouterr().out
