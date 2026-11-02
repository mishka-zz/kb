#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Mike Volokhov
# SPDX-License-Identifier: BSD-2-Clause

"""What this project knows, and what is open.

    kb                             where the project stands
    kb note "a sentence"           catch it, and get an identity back
    kb note 12 "more"              add to what is already caught
    kb set 12 outcome "..."        write one field, and leave the rest alone
    kb close 12 [moot|refused]     date it and move it, if the place will hold it
    kb find <words> [options]      search everything, and read what comes back
    kb rules                       every guideline, in one screen
    kb check                       whether the record can still be walked
    kb stale                       which facts have lost their evidence
    kb stale --dry-run             what it would run, and what rests on prose
    kb --help                      this, from anywhere in a command line
    KB_RECORD=... kb               which record, where the directory is not
                                   found from where you stand

The record is found from the current directory upward: the first `kb/` holding
a `project.md`, or the directory you are in if it is the record itself. That
file names what the record is about - which trees it cites, which documents it
holds to a citation - in the same flat `key: value` form as an entry; the tool
itself belongs to no project.

What `find` takes, none of which is discoverable from what it prints:

    --near <id>       one entry whole, and a card for everything a link away
    --full            the body of every hit, not just the head - under
                      --near, every neighbour whole rather than as a card
    --field <k>=<v>   only entries whose field k contains v; `place` counts
    --fields <a,b>    print these fields and no others
    --limit <n>       hits a page, default ten - under --near, the whole set
    --page <n>        a later page of the same search
    --floor <share>   drop a hit below this share of the question, which is
                      otherwise reported as thin rather than hidden

Hand out an identity, search, and keep the record walkable. Shaping a draft,
deciding it is finished, cutting it down, retiring it - judgement, and not this
tool's work. Writing a field the writer decided on, and moving an entry to the
place it was decided to go, are mechanics, and a hand doing them by `replace`
and `mv` has lost the head's closing fence and left a closure undated.

**Nothing here is stored that could be searched for instead.** No index, no
summary, no table of contents: a stored answer goes stale the moment the record
moves under it, and a search cannot, because it computes rather than keeps.

Standard library only. Nothing reads git.
"""

from __future__ import annotations

import ast
import fnmatch
import math
import os
import re
import shutil
import signal
import statistics
import subprocess
import sys
import textwrap
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

#: How hard a long entry is held back in a search, as the exponent on the ratio
#: between the median entry's prose and its own. Zero is no penalty at all. It
#: sits where the penalty still costs nothing measurable: past it the longest
#: entries begin to lose their own subject, and below it the widest go on
#: reaching the top of questions they have no part in. Measured on the record
#: this tool grew in, not re-measured on each one it serves.
BREADTH = 0.2

#: Where the tool lives, which is not where the record lives. `schema.md`
#: beside this file says what a field means, and an error pointing a reader
#: there needs the path.
HERE = Path(__file__).resolve().parent
#: What a record carries at its root to say what it is about. Its presence is
#: also how the record is found from the current directory upward.
PROJECT = "project.md"

#: The record in hand, and the project around it. Set by :func:`configure`
#: before any command runs; the defaults serve a record that says nothing
#: about itself, and the tests point them at a temporary one.
ROOT = Path.cwd() / "kb"
REPO = ROOT.parent
KNOWN, ARCHIVE = ROOT / "known", ROOT / "archive"

#: Where a piece of work is in its life. The directory is the state; no field
#: holds a copy, so the two cannot disagree and nothing has to be filed after.
QUEUE = ("noted", "analyzed", "scoped", "done", "moot", "refused")
TERMINAL = ("done", "moot", "refused")
KINDS = ("work", "fact", "decision")

#: The subject holding how to work here. Named apart because `kb rules`
#: prints it whole, and because a rule that has to be looked up does not fire.
GUIDELINES = "guidelines"

#: Crockford's alphabet - no I, L, O or U, so nothing reads as a one or a zero
#: and an identity can be said aloud. Counted up rather than drawn, so a
#: listing sorts into the order things were learned.
ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
#: Where the count opens: `10`, the first two-character number - `1A` is the
#: first identity handed out from it. A new one carries both a digit and a
#: letter, in any order: all digits reads as a plain number, all letters as
#: initials beside the abbreviations this record is full of, and `note` skips
#: whatever the count offers of either. Two characters is the shortest that
#: can hold both. The ones already handed out keep what they were given.
FIRST = len(ALPHABET)

IDENTITY = re.compile(r"^[" + ALPHABET + r"]{2,}(?:\.\d+)*$")
REFERENCE = re.compile(r"\[\[([0-9A-Z][0-9A-Z.]+)\]\]")

#: What a provenance is, by its first word. The kind decides its upkeep: the
#: first two lose their evidence loudly, the rest silently or not at all.
PROVENANCE = ("test", "gate", "source", "cited", "measured", "judged")
RERUN = ("test", "gate")

#: Where one kind of evidence ends and the next begins, in a field carrying
#: several: a kind's own word and its colon, starting a word - after the start,
#: a space or a bracket, so never inside a path. A record writes the boundary as
#: `; measured:`, `. test:`, `and gate:` or `The gate:`, and each is the same
#: boundary.
SEGMENT = re.compile(r"(?:;\s*|(?<=[\s(]))(?=(?:" + "|".join(PROVENANCE) + r"):)")


def _evidence(value: str) -> list[tuple[str, str]]:
    """A provenance or an outcome as the kinds it carries, each with its text.

    One field often rests on more than one kind - the tests that hold a fact and
    the measurement that found it - and each kind keeps its own upkeep, so a path
    written under `measured:` is never handed to a test runner because the field
    opened with `test:`.
    """
    return [(part.split(":", 1)[0].strip(), part) for part in SEGMENT.split(value) if part.strip()]

#: Every field an entry may carry, and the set is closed. Which fields a place
#: *requires* is decided in `check`; this is only what a name may be.
#:
#: Closed for one reason worth more than tidiness. A field carried on indented
#: lines becomes an ordinary field again the moment the indent is lost - to a
#: careless rewrite, to a tool that strips leading whitespace - and the line it
#: becomes is `src/parse_test.go::TestName: ...`, which parses. Against
#: an open set that is silent, and it lands on citations, which is where these
#: fields carry their weight. Against a closed one it is a fault naming the
#: line. `note` already flattens what it writes for the same reason.
#:
#: It catches the fault from the other side too: `critereon` is otherwise an
#: entry with no criterion and nothing to say so.
FIELDS = ("id", "title", "kind", "noted", "tags", "related", "legacy",
          "provenance", "criterion", "because", "outcome", "closed",
          "decided", "working")

#: What the project owns, so a citation naming one of these can be checked to
#: still be there. Anything else is a reference, not a path. Third-party text
#: kept in the tree - a standard, a vendored source - belongs here too if it is
#: cited, since a citation into a document that has moved is a fault like any
#: other. `project.md` field `owned`; the record's own directory is always in.
OWNED: tuple[str, ...] = ("kb",)
#: Of those, the trees a working copy may legitimately be without - released on
#: their own cadence, cloned on their own. A citation into a tree that is
#: **entirely** absent says nothing about the record and is passed over; a
#: missing file inside a tree that is here is a citation gone bad. The test is
#: on the tree and never on anything below it, so a directory that was deleted
#: out of a tree still fails, which is the case worth catching. Field `outside`.
OUTSIDE: tuple[str, ...] = ()


def _paths(owned: tuple[str, ...]) -> re.Pattern[str]:
    """A citation of a file in one of ``owned``, from the repository root.

    The tree's name opens the path: one following a word and a slash is
    somewhere inside another path - a URL, a tree nobody owns - and a citation
    of nothing here.
    """
    return re.compile(r"(?<![\w-]/)(?<![\w-])((?:" + "|".join(map(re.escape, owned))
                      + r")/[\w./:-]*[\w])")


PATH = _paths(OWNED)

#: `page.py:82`, `page.py:126-207` - the form this project cites source in.
LINES = re.compile(r":\d+(?:-\d+)?$")
#: Something named *inside* a file: a filename and `::`, or `::` opening a word
#: where the file was left to the sentence before. Used to catch the citation
#: written with no path to reach it by, which is one nothing here runs.
#:
#: `::` is also how C++ spells a scope and how a Go doc comment reaches a
#: method, and prose here carries `std::vector` and `header::Field` alike. What
#: separates them is the extension: a citation names a *file*, a scope names a
#: namespace, and neither pattern here reaches the other.
NODE = re.compile(r"[\w./-]+\.\w+::[\w:]+|(?<![\w:./-])::[\w:]+")

#: A fenced block, which is quoted or run rather than claimed. A body pasting a
#: test address is pasting a command, and one about citations has to be able to
#: write the form it is about - neither is a claim that the name is there, and
#: holding them to one would rewrite a working command to quiet a checker. A
#: fence nobody closed is left alone rather than swallowing the rest of the
#: entry, because reporting is the safe direction.
FENCE = re.compile(r"^[ \t]*(```|~~~).*?^[ \t]*\1", re.MULTILINE | re.DOTALL)

#: Where a reference may be written, and so where `check` resolves one. A
#: `[[1A]]` written somewhere that ships without the record is a citation its
#: own readers cannot resolve, so a project names only what travels with the
#: record. Field `citers`; the record's own directory is always in.
CITERS: tuple[str, ...] = ("kb",)
#: Where an answer may already live. The source is searched because the rule
#: everywhere this tool is used puts what the code cannot say beside the code -
#: a record searching only itself looks in the wrong place. Field `source`.
SOURCE: tuple[str, ...] = ()
#: Directory names that search passes over inside those trees - a copy of
#: somebody else's code vendored into one, which answers nothing about ours and
#: outnumbers it. Field `skip`.
SKIP: tuple[str, ...] = ()
#: The documents read for what is true *now*, and so held to a citation the way
#: an entry is. `load` walks the entries and nothing walked these, so a name
#: written in the page a reader opens first was held to nothing at all. A
#: record of a day - an archive, a dated plan - is never read for the current
#: state, and holding it would be a listing that never empties, which is one
#: nobody reads. Field `documents`.
DOCUMENTS: tuple[str, ...] = ()
#: The subjects in `known/` that hold what somebody *else's* software does -
#: an engine, a client, a kernel, the behaviour no document decides. Everything
#: else there is ours to change; these are measurements of behaviour we do not
#: control, and the only way to find one wrong is to be bitten by it. Field
#: `theirs`.
THEIRS: tuple[str, ...] = ()
#: The command a record carries under `run/` for each kind of cited test, by the
#: name of the file the citation names - a pattern and a command per kind, in
#: the order they are tried. `kb.skel/run/README.md` is the contract, and a
#: sample comes with the skeleton.
#:
#: The table is the whole of the routing, and the record's: which files are
#: tests and what runs them is the project's to say, so the tool names neither.
#: A path it does not hold is handed to no command: a command asked to run what
#: is not its test says red, and a red that is about the citation reads as one
#: about the code. Such a path under `test:` is most often the code a test
#: covers or the helper it drives, mentioned beside the test in a sentence
#: about it. Field `runners`, written `test_*.py run-pytest, *_test.go run-go-test`.
RUNNERS: dict[str, str] = {}

#: Below this share of a question, the best hit is thin enough to say so. It
#: reports rather than hides: dropping an entry for sharing few words with the
#: question loses it silently, which is the one failure this record refuses.
#: `--floor` is there for a caller that would rather have the cut.
THIN = 0.35

#: A measured quantity written into prose - a rate, a size, a time. Where an
#: entry carries one and nothing it cites re-runs, that figure is the one thing
#: in the record nothing re-derives. A project's bars have their own units, so
#: the pattern is the field `figure`, and this is what it says when it says
#: nothing.
FIGURE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|per cent|ppm|[KMGT]i?B|ms|\u00b5s|s)\b")

WORD = re.compile(r"\w[\w.-]*")
STOPWORD = set("a an and the is are of to in on it its that this for by with as "
               "not no or be was were which what when where how do does".split())


def words(text: str) -> set[str]:
    return {w.strip(".-") for w in WORD.findall(text.lower())} - STOPWORD - {""}


# ---------------------------------------------------------------- the record

def _record() -> Path:
    """The record this command is about.

    `$KB_RECORD` if it is set. Otherwise the directory you stand in if it is a
    record itself, else the first `kb/` holding a `project.md` from here upward
    - which is how a command works from anywhere inside a project, the way a
    version-control command does. A record is recognised by that file and not
    by its name alone, because a directory called `kb/` is not rare.
    """
    told = os.environ.get("KB_RECORD")
    if told:
        root = Path(told).expanduser().resolve()
        if not root.is_dir():
            sys.exit(f"$KB_RECORD is {told}, which is not a directory")
        return root
    here = Path.cwd().resolve()
    for above in (here, *here.parents):
        if (above / PROJECT).is_file() and (above / "noted").is_dir():
            return above
        if (above / "kb" / PROJECT).is_file():
            return above / "kb"
    sys.exit(f"no record here: no kb/{PROJECT} in this directory or above it, "
             "and $KB_RECORD is not set")


def _project(root: Path) -> dict[str, str]:
    """What the record says about itself, from `project.md` - the same flat
    `key: value` head an entry carries, so there is one format to know."""
    page = root / PROJECT
    if not page.is_file():
        return {}
    fields, _, broken = _head(page.read_text(encoding="utf-8", errors="replace"), ())
    if broken:
        sys.exit("\n".join(f"{page}: {fault}" for fault in broken))
    return fields or {}


def configure(root: Path, fields: dict[str, str]) -> None:
    """Point the tool at a record, and read what the record says it is about.

    Everything project-shaped is a module global set here and nowhere else, so
    the tool itself belongs to no project and two records on one machine share
    one copy of it. The record's own directory is always owned and always a
    citer, whatever the file says, since an entry cites its neighbours.
    """
    global ROOT, REPO, KNOWN, ARCHIVE, OWNED, OUTSIDE, PATH, CITERS, SOURCE
    global DOCUMENTS, THEIRS, FIGURE, SKIP, RUNNERS
    ROOT, REPO = root, root.parent
    KNOWN, ARCHIVE = root / "known", root / "archive"
    mine = root.name

    def trees(name: str) -> list[str]:
        # `src/` and `./src` are `src`: a citation never carries either form,
        # and kept, one would match nothing and switch the check off silently.
        return [re.sub(r"^(?:\./)+", "", tree).rstrip("/") or "." for tree in
                _list(fields.get(name, ""))]

    OWNED = tuple(dict.fromkeys([*trees("owned"), mine]))
    OUTSIDE = tuple(trees("outside"))
    PATH = _paths(OWNED)
    CITERS = tuple(dict.fromkeys([mine, *trees("citers")]))
    SOURCE = tuple(trees("source"))
    SKIP = tuple(trees("skip"))
    DOCUMENTS = tuple(trees("documents"))
    THEIRS = tuple(_list(fields.get("theirs", "")))
    if fields.get("figure"):
        FIGURE = re.compile(fields["figure"])
    RUNNERS = {}
    for pair in _list(fields.get("runners", "")):
        pattern, *command = pair.split()
        if len(command) != 1 or "/" in command[0]:
            sys.exit(f"{root / PROJECT}: runners: {pair!r} is not a pattern and the name "
                     "of a command under run/ - `test_*.py run-pytest`")
        RUNNERS[pattern] = command[0]


@dataclass
class Entry:
    id: str
    title: str
    place: str
    path: Path
    fields: dict[str, str]
    body: str

    @property
    def kind(self) -> str:
        return self.fields.get("kind", "")

    @property
    def tags(self) -> list[str]:
        return _list(self.fields.get("tags", ""))

    @property
    def known(self) -> bool:
        """The reference rather than the queue.

        Asked of the path: `known/` holds whatever subjects somebody made, and
        one named after a queue directory would otherwise answer as that place.
        """
        return self.path.is_relative_to(KNOWN)

    @property
    def searchable(self) -> str:
        return f"{self.title} {' '.join(self.fields.values())} {self.body}"

    def __str__(self) -> str:
        return f"{self.id:<5} {self.title}"

    def scanned(self, indent: int = 0) -> str:
        """The entry as one line of a listing, folded to the terminal if it must be.

        A listing is read by running an eye down the identities, and an entry
        whose title takes six lines of it hides the ones after it. Nothing is
        lost by folding: a title long enough to be cut is a draft's, and
        `find --near` prints it whole.
        """
        room = shutil.get_terminal_size(fallback=(100, 24)).columns - indent - 8
        if len(self.title) <= max(room, 40):
            return str(self)
        kept = self.title[: max(room, 40)].rsplit(" ", 1)[0]
        return f"{self.id:<5} {kept} …"


def _list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _number(identity: str) -> int:
    value = 0
    for character in identity.split(".")[0]:
        value = value * len(ALPHABET) + ALPHABET.index(character)
    return value


def _identity(value: int) -> str:
    digits = ""
    while value:
        value, remainder = divmod(value, len(ALPHABET))
        digits = ALPHABET[remainder] + digits
    return digits


def _mixed(identity: str) -> bool:
    """Both a digit and a letter somewhere in it."""
    characters = set(identity)
    return bool(characters & set(ALPHABET[:10])) and bool(characters & set(ALPHABET[10:]))


def _head(text: str, names: tuple[str, ...]) -> tuple[dict[str, str] | None, str, list[str]]:
    """The fields between the fences, the prose after them, and what did not
    parse as one. The fields are None where there is no head to read at all.

    ``names`` is the closed set a field may be called; empty, any name goes,
    which is how `project.md` is read - it is the one file whose vocabulary is
    the tool's rather than the record's, and this docstring's neighbours say
    what each of its fields means.
    """
    fields: dict[str, str] = {}
    broken: list[str] = []
    if text.endswith("\n---"):
        # A closing fence with no newline after it, as an editor that strips
        # the last one leaves it, closes the head all the same.
        text += "\n"
    if not text.startswith("---\n"):
        return None, "", ["does not open with a fence"]
    head, fence, body = text[4:].partition("\n---\n")
    if not fence:
        return None, "", ["the fields are never closed"]
    previous = None
    for line in head.split("\n"):
        if line[:1].isspace() and line.strip():
            # A field carried on to the next line, joined with one space.
            # `outcome` and `because` are paragraphs by the time an entry
            # closes, and a paragraph held on one physical line is one nobody
            # can read in a diff.
            #
            # Tested before the colon, so a continuation may carry one - a
            # citation, a ratio, a time - without reading as a new field.
            if previous is None:
                broken.append(f"{line.strip()[:40]!r} is indented under no field")
                continue
            fields[previous] = f"{fields[previous]} {line.strip()}".strip()
            continue
        key, colon, value = line.partition(":")
        if colon and key.strip() and (not names or key.strip() in names):
            previous = key.strip()
            if previous in fields:
                # Silently, otherwise: an entry written with one `outcome` per
                # kind of evidence keeps the last, and the citations in the
                # others reach neither `check` nor `stale`.
                broken.append(
                    f"{previous!r} is written twice - the second replaces the "
                    "first, and a field carried on indented lines is how one of "
                    "them holds several paragraphs"
                )
            fields[previous] = value.strip()
        elif colon and key.strip() and " " not in key.strip():
            previous = None
            broken.append(
                f"{key.strip()!r} is not a field this format has - a carried "
                "line that lost its indent reads exactly like this"
            )
        elif line.strip():
            previous = None
            broken.append(f"{line.strip()[:40]!r} is neither a field nor prose")
    return fields, body, broken


@dataclass
class Parsed:
    """One file read as an entry: its fields, or None where there is no head."""
    fields: dict[str, str] | None
    body: str
    faults: list[str]


def _parse(at: Path, text: str) -> Parsed:
    """The fields and the prose of one entry, and what is wrong with its form.

    One reader for everything that reads an entry, `set` and `close` included:
    a writer that checked its own output with a second parser would pass a file
    the record then reads differently.
    """
    fields, body, faults = _head(text, FIELDS)
    return Parsed(fields, body, [f"{at}: {fault}" for fault in faults])


def load() -> tuple[list[Entry], list[str]]:
    """Every entry. One format everywhere - a file, fields, then prose."""
    entries, broken = [], []
    found = [(p, p.relative_to(ROOT).parts[0]) for place in QUEUE
             for p in sorted((ROOT / place).rglob("*.md"))]
    found += [(p, str(p.parent.relative_to(KNOWN))) for p in sorted(KNOWN.rglob("*.md"))]

    for path, place in found:
        at = path.relative_to(ROOT)
        if place == ".":
            broken.append(f"{at}: sits directly in known/ rather than under a subject")
            continue
        parsed = _parse(at, path.read_text(encoding="utf-8", errors="replace"))
        broken += parsed.faults
        if parsed.fields is None:
            continue
        fields, body = dict(parsed.fields), parsed.body
        identity, title = fields.pop("id", ""), fields.pop("title", "")
        if not identity or not title:
            broken.append(f"{at}: no id, or no title")
            continue
        if not IDENTITY.match(identity):
            broken.append(f"{at}: {identity!r} is not an identity - see the alphabet")
            continue
        if not path.name.startswith(f"{identity}-"):
            broken.append(f"{at}: holds {identity}, which its own name does not")
        entries.append(Entry(identity, title, place, path, fields, body))
    return entries, broken


def resolves(cited: str, known: set[str]) -> bool:
    """Whether a citation leads somewhere across a split or a merge.

    An entry that grew into `12.1` and `12.2` is still reached by `[[12]]`, and
    parts merged back into `12` are still reached by `[[12.1]]`. Each step is
    exact: going up looks for that parent itself, never for whatever else is
    left of its family, so a citation never lands on an unrelated sibling.
    """
    if cited in known or any(other.startswith(cited + ".") for other in known):
        return True
    while "." in cited:
        cited = cited.rsplit(".", 1)[0]
        if cited in known:
            return True
    return False


# ------------------------------------------------------------------ identity

def _named_by_files() -> set[str]:
    """Every identity a file in the record is named after, parsed or not.

    `load` drops a file it cannot read as an entry, and `check` names it - but
    its identity is still in use, and handed out again it becomes two files
    holding one identity the day the first is mended.
    """
    places = [ROOT / place for place in QUEUE] + [KNOWN]
    return {path.name.split("-", 1)[0] for place in places if place.is_dir()
            for path in place.rglob("*.md")
            if IDENTITY.match(path.name.split("-", 1)[0])}


def note(argv: list[str]) -> None:
    entries, _ = load()
    loaded = {e.id for e in entries}
    if argv and argv[0].upper() in loaded:
        return _append(argv[0].upper(), " ".join(argv[1:]), entries)
    taken = loaded | _named_by_files()

    text = " ".join(argv).strip()
    if not text:
        sys.exit("a sentence is the one thing a note cannot be without")
    # Flattened before it reaches the head: a wrapped paragraph is the ordinary
    # way to catch a thought, and left alone its later lines are read back as
    # fields nobody wrote - a note that declares itself a fact.
    flat = " ".join(text.split())
    # The whole sentence, however long. What a note is for is the thought caught
    # at minute forty, and its tail is the part carrying what was noticed - so a
    # length that suits a listing is not a reason to throw the end of it away.
    # The filename is what needs a bound, and the slug has its own.
    title = flat
    slug = _slug(title)

    value = max([_number(i) for i in taken] + [FIRST - 1]) + 1
    # A record is recognised by its project.md, so one copied in by hand may be
    # short of the directory a note goes to and of nothing else.
    (ROOT / "noted").mkdir(exist_ok=True)
    while True:
        identity = _identity(value)
        if not _mixed(identity) or identity in taken:
            value += 1
            continue
        path = ROOT / "noted" / f"{identity}-{slug}.md"
        if not list((ROOT / "noted").glob(f"{identity}-*")):
            try:
                with path.open("x", encoding="utf-8") as handle:
                    handle.write(f"---\nid: {identity}\ntitle: {title}\n"
                                 f"noted: {date.today().isoformat()}\ntags: \n---\n\n{text}\n")
                break
            except FileExistsError:
                pass
        value += 1

    print(f"{identity}  {path.relative_to(REPO)}")
    _already(entries, words(flat))


def _slug(title: str) -> str:
    """The filename's share of the title: whole words, and not too many.

    A hard cut lands mid-word and leaves a name trailing a connective - `-by-the`
    was a real one - so words are taken whole until the budget is spent, and
    stopwords left dangling at the end are dropped. A single word longer than
    the whole budget is cut anyway, there being nothing better in it.
    """
    parts = re.sub(r"[\W_]+", "-", title.lower()).strip("-").split("-")
    kept: list[str] = []
    for part in parts:
        if kept and len("-".join([*kept, part])) > 48:
            break
        kept.append(part)
    while len(kept) > 1 and kept[-1] in STOPWORD:
        kept.pop()
    # A title of nothing but punctuation still names a file someone can type.
    return "-".join(kept)[:48] or "note"


def _already(entries: list[Entry], terms: set[str]) -> None:
    """What is here already, printed without being asked for.

    The failure this answers was not a bad search - it was nobody thinking to
    search. So it happens on the way past rather than on remembering to.

    **Each hit carries its score**, as it does under `find`, and the score says
    how much of the *question* an entry answered rather than whether it is about
    the same thing. Those come apart: an entry using all the words somewhere
    scores full marks against one that is exactly on the subject and happens not
    to use one of them. Printing the number does not settle which is which - it
    is what lets a reader see the difference instead of inferring an authority
    the order does not carry.
    """
    near = _rank(entries, terms)[:4]
    if near:
        print("\nalready recorded:")
        for score, entry in near:
            print(f"  {score:4.0%}  {entry.scanned(20)}   [{entry.place}]")
    for where, line, text in _in_source(terms, 3):
        print(f"\n  {where}:{line}  {text.strip()[:90]}")


def _in_source(terms: set[str], cap: int) -> list[tuple[str, int, str]]:
    if len(terms) < 2:
        return []
    scored = []
    for tree in SOURCE:
        start = REPO / tree
        pages = [start] if start.is_file() else [p for p in start.rglob("*")
                                                 if p.suffix in (".py", ".go", ".md")
                                                 and not set(SKIP) & set(p.parts)
                                                 and p.is_file()]
        for path in pages:
            best, count = None, 0
            for number, text in enumerate(path.read_text(encoding="utf-8",
                                                         errors="replace").split("\n"), 1):
                hit = len(terms & words(text))
                if hit >= 2:
                    count += 1
                    if best is None or hit > best[2]:
                        best = (number, text, hit)
            if best:
                scored.append((best[2], count, str(path.relative_to(REPO)), best))
    scored.sort(key=lambda row: (-row[0], -row[1]))
    return [(where, best[0], best[1]) for _, _, where, best in scored[:cap]]


def _append(identity: str, text: str, entries: list[Entry]) -> None:
    if not text.strip():
        sys.exit("nothing to add")
    entry = next(e for e in entries if e.id == identity)
    try:
        body = _read(entry.path).rstrip()
    except FileNotFoundError:
        sys.exit(f"{entry.path} has moved since it was read; run again")
    temporary = entry.path.with_suffix(".md.writing")
    temporary.write_text(f"{body}\n\n*{date.today().isoformat()}* - {text.strip()}\n",
                         encoding="utf-8")
    temporary.replace(entry.path)
    print(f"{identity}  {entry.path.relative_to(REPO)}")


# ------------------------------------------------------------------- writing

#: Where a field carried on indented lines wraps. A title is left on one line,
#: as `note` writes it, and a listing folds it.
WIDTH = 78


def _head_line(name: str, value: str) -> str:
    if name == "title":
        return f"title: {value}"
    # Only at spaces: a citation broken at a hyphen or inside a word is one
    # nothing reads, and `check` names the one broken after its colons.
    return textwrap.fill(f"{name}: {value}", WIDTH, subsequent_indent="    ",
                         break_long_words=False, break_on_hyphens=False)


def _with(entry: Entry, text: str, name: str, value: str) -> str:
    """The file with one field written, every other line of it as it was.

    Edited rather than regenerated: an entry rewritten whole loses whatever
    the writer did not think to carry across. The result is read back by the
    one parser the record uses and refused unless the field reads as written
    and nothing else in the head or the prose moved - a replace that lost the
    head's closing fence reads as a head swallowing the body, and this is
    where that is caught rather than at the next `check`.
    """
    at = entry.path.relative_to(ROOT)
    if text.endswith("\n---"):
        text += "\n"           # as `_head` reads it, so the two split alike
    before = _parse(at, text)
    if before.fields is None:
        # `load` read it a moment ago, so something else is writing to it.
        sys.exit(f"{at} has changed since it was read; nothing written")
    head, _, body = text[4:].partition("\n---\n")
    lines, kept, carried, written = head.split("\n"), [], False, False
    blank: list[str] = []
    if sum(not line[:1].isspace() and line.partition(":")[0].strip() == name
           for line in lines) > 1:
        # The parser keeps the last and `check` names the pair; which of the two
        # was meant is the writer's to say.
        sys.exit(f"{at}: {name} is written twice; mend it by hand first")
    for line in lines:
        if carried:
            # The parser carries a field across a blank line, so what follows
            # one indented is still the old value; a blank before anything else
            # is layout, and stays.
            if not line.strip():
                blank.append(line)
                continue
            if line[:1].isspace():
                blank = []
                continue
            kept += blank
            blank, carried = [], False
        if not line[:1].isspace() and line.partition(":")[0].strip() == name:
            kept.append(_head_line(name, value))
            carried = written = True
            continue
        kept.append(line)
    kept += blank
    if not written:
        kept.append(_head_line(name, value))
    result = "---\n" + "\n".join(kept) + "\n---\n" + body

    after = _parse(at, result)
    wanted = {**before.fields, name: value}
    if after.fields != wanted or after.body != before.body \
            or set(after.faults) - set(before.faults):
        sys.exit(f"{at}: writing {name} would change more than {name}; nothing written")
    return result


def _placed(entry: Entry, text: str, place: str, target: Path,
            entries: list[Entry]) -> tuple[list[str], Entry | None]:
    """Every fault `check` would find in ``text`` standing at ``target``, and
    the entry it would be there.

    What `load` collects on the way in, what the place asks of the fields, and
    whether each `related` and each `[[id]]` leads somewhere - an entry `load`
    would drop, for a blank title, being the worst of them: its identity then
    reads as free.
    """
    at = target.relative_to(ROOT)
    parsed = _parse(at, text)
    fields = dict(parsed.fields or {})
    identity, title = fields.pop("id", ""), fields.pop("title", "")
    if identity != entry.id or not title:
        return [*parsed.faults, f"{at}: no id, or no title - the record would drop it"], None
    standing = Entry(entry.id, title, place, target, fields, parsed.body)
    known = {e.id for e in entries}
    faults = parsed.faults + _held(standing, entries)
    faults += [f"{at}: related {cited} leads nowhere"
               for cited in _list(fields.get("related", "")) if not resolves(cited, known)]
    faults += [f"{at}: [[{cited}]] leads nowhere"
               for cited in REFERENCE.findall(text)
               if IDENTITY.match(cited) and not resolves(cited, known)]
    return faults, standing


def _beside(entry: Entry, standing: Entry, entries: list[Entry]) -> Counter[str]:
    """What the entries linked to ``entry`` break with it standing as ``standing``.

    The rules that reach across entries run along links - a measurement is held
    to relating to a claim in `known/status/` - so a move that faults another
    entry faults one linked to it.
    """
    moved = [standing if other is entry else other for other in entries]
    by_id = {other.id: other for other in moved}
    return Counter(fault for near in _linked(entries, entry.id)
                   for fault in _held(by_id[near], moved))


def _read(path: Path) -> str:
    """The file exactly, or a refusal: a byte decoded as a replacement would be
    written back as one, changing a line nobody asked to change."""
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as error:
        sys.exit(f"{path.relative_to(REPO)}: byte {error.start} is not UTF-8, and writing "
                 "the file back would change it; mend it by hand")
    if "\r" in text:
        sys.exit(f"{path.relative_to(REPO)}: its lines end in CR LF, and writing it back "
                 "would change every one of them; convert it to LF first")
    return text


def _replace(path: Path, text: str) -> None:
    temporary = path.with_suffix(".md.writing")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _entry(identity: str) -> tuple[Entry, list[Entry]]:
    entries, _ = load()
    found = [e for e in entries if e.id == identity.upper()]
    if len(found) != 1:
        sys.exit(f"no entry {identity}" if not found else
                 f"{identity} is held by {len(found)} files - run check")
    return found[0], entries


def set_field(argv: list[str]) -> None:
    """One field of one entry, written without touching the rest of it."""
    if len(argv) < 3:
        sys.exit("kb set <id> <field> <value>")
    name, value = argv[1], " ".join(" ".join(argv[2:]).split())
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        sys.exit(f"the value for {name} carries a byte that is not UTF-8; nothing written")
    if name not in FIELDS or name == "id":
        sys.exit(f"{name!r} is not a field set can write - one of "
                 f"{[f for f in FIELDS if f != 'id']}; an identity is the file's name")
    entry, entries = _entry(argv[0])
    text = _read(entry.path)
    written = _with(entry, text, name, value)
    # Held to what the entry's own place asks, as `close` holds a move: a value
    # `check` would refuse is caught here rather than the next time it runs.
    # Only what the write adds - a fault already there is somebody else's to
    # mend - and counted, since a second copy of a fault is a second fault.
    #
    # One trade is let through: a field written may ask for another the entry
    # does not carry yet - `kind work` asks for a criterion - where the fault
    # it mends is the one it opens in its place. What the write adds is then
    # only fields still to be written, and the entry is no further from
    # walkable than it was, so the order the fields are set in decides nothing.
    after, standing = _placed(entry, written, entry.place, entry.path, entries)
    before, _ = _placed(entry, text, entry.place, entry.path, entries)
    added = Counter(after) - Counter(before)
    if added and len(after) <= len(before) and standing is not None:
        added -= Counter(_wanting(standing, entries))
    if added:
        sys.exit("\n".join([*sorted(added), f"{entry.id}: {name} not written"]))
    _replace(entry.path, written)
    print(f"{entry.id}  {entry.path.relative_to(REPO)}")
    # What was replaced is said, so a field overwritten by mistake is one
    # somebody can put back.
    was = entry.title if name == "title" else entry.fields.get(name, "")
    if was and was != value:
        print(f"    {name} was: {was}")


def close(argv: list[str]) -> None:
    """Date an entry and move it to a terminal place, if that place will hold it.

    What the entry says - the outcome, the reason it was put down - is the
    writer's, and is written first with `set`. This is the rest: `closed:`
    today where no date is written, and the move. The entry is held to what
    `check` asks of the place it is going to before anything is written - its
    form, its fields and where its `related` leads - so a closure with no
    outcome, or an outcome naming no kind of evidence, stays where it was and
    says why.
    """
    if not argv or len(argv) > 2:
        sys.exit("kb close <id> [moot|refused]")
    where = argv[1] if len(argv) == 2 else "done"
    if where not in TERMINAL:
        sys.exit(f"{where!r} is not a place an entry closes to - one of {list(TERMINAL)}")
    entry, entries = _entry(argv[0])
    if entry.place in TERMINAL:
        sys.exit(f"{entry.id} is already {entry.place}")
    target = ROOT / where / entry.path.name
    if target.exists():
        sys.exit(f"{target.relative_to(REPO)} is there already")
    text = _read(entry.path)
    if not entry.fields.get("closed"):
        text = _with(entry, text, "closed", date.today().isoformat())
    faults, standing = _placed(entry, text, where, target, entries)
    if standing is not None:
        faults += list(_beside(entry, standing, entries) - _beside(entry, entry, entries))
    if faults:
        sys.exit("\n".join([*faults, f"{entry.id} stays in {entry.place}"]))
    # Moved first and dated second: the move is the one atomic step, and an
    # entry stopped between the two is a `done` with no date, which `check`
    # names, rather than two files holding one identity.
    # A terminal place is one of the tool's names, so a record that never
    # closed an entry there is short of the directory and nothing else.
    target.parent.mkdir(exist_ok=True)
    entry.path.replace(target)
    _replace(target, text)
    print(f"{entry.id}  {target.relative_to(REPO)}")


# ----------------------------------------------------------------- retrieval

def _rank(entries: list[Entry], terms: set[str]) -> list[tuple[float, Entry]]:
    """The share of a question an entry answers, weighted by how rare each word
    of it is - so a word every entry carries counts for little and a word
    nothing carries counts for most.

    Not term frequency times inverse document frequency: a repeated word says
    nothing here, entries being one claim each, so `words` is a set and only the
    rarity survives. What that buys is a score bounded by one and readable as a
    proportion, where a bare sum of weights grows with the length of the
    question and means nothing across two of them.

    Settled knowledge outranks an unshaped note on a tie, because a scratchpad
    promises nothing.

    A long entry is held back, because breadth is not an answer. The share above
    asks only how much of the question was covered, so an entry whose prose
    spans the record answers a part of every question ever asked and arrives
    beside the entries that are about it. The measure is the body, not
    everything searched: a shaped entry carries a criterion and a provenance
    and must not be held back for having them. Nothing is ever pushed up, only
    held back, so two entries saying the same thing still tie and the tie still
    goes to the settled one. `BREADTH` is the exponent.
    """
    if not terms:
        return [(0.0, e) for e in entries]
    #: Read once per entry rather than once per entry per term. The median of
    #: these is what a long entry is long against, so it moves with the record
    #: instead of being a length written down.
    vocabulary = {id(e): words(e.searchable) for e in entries}
    prose = {id(e): len(words(e.body)) for e in entries}
    middle = statistics.median(prose.values()) if entries else 1.0
    holding = {t: sum(1 for e in entries if t in vocabulary[id(e)]) for t in terms}
    #: A term nothing holds weighs the most, not nothing. Dropping it would take
    #: the question's unanswered half out of the denominator, and the one entry
    #: holding the one common word would come back as a whole answer.
    weight = {t: math.log(max(len(entries), 1) / max(n, 1)) + 1
              for t, n in holding.items()}
    #: What a hit would score if it held every term asked for. Scoring against it
    #: rather than against the best hit is what lets the search answer *nothing*:
    #: a lone rare word matches loudly, and against the whole question it is a
    #: third of an answer and says so.
    asked = sum(weight.values()) or 1.0
    scored = []
    for entry in entries:
        held = terms & vocabulary[id(entry)]
        if held:
            share = sum(weight[t] for t in held) / asked
            spread = max(prose[id(entry)], 1)
            held_back = min(1.0, max(middle, 1.0) / spread) ** BREADTH
            scored.append((share * held_back, entry))
    scored.sort(key=lambda row: (-row[0], row[1].place == "noted", row[1].id))
    return scored


def find(argv: list[str]) -> None:
    terms, fields, show, near = [], [], None, None
    limit, page, full, floor = 0, 1, False, 0.0
    rest = list(argv)
    while rest:
        word = rest.pop(0)
        if word == "--full":
            full = True
        elif word in ("--near", "--field", "--fields", "--limit", "--page",
                      "--floor") and rest:
            value = rest.pop(0)
            if word == "--near":
                near = value.upper()
            elif word == "--field":
                fields.append(value)
            elif word == "--fields":
                show = _list(value)
            elif word == "--floor":
                try:
                    floor = float(value)
                except ValueError:
                    sys.exit(f"--floor {value}: a share is a number, 0.35 for 35%")
            else:
                if not value.isdecimal() or int(value) < 1:
                    sys.exit(f"{word} {value}: a count, 1 or more")
                if word == "--limit":
                    limit = int(value)
                else:
                    page = int(value)
        elif word.startswith("--"):
            sys.exit(f"{word}: not an option, or missing its value")
        else:
            terms.append(word.lower())

    entries, _ = load()
    if near:
        hits = [(0.0, e) for e in _around(entries, near)]
    else:
        for clause in fields:
            name, _, value = clause.partition("=")
            entries = [e for e in entries
                       if value.lower() in e.fields.get(name, "").lower()
                       or (name == "place" and value.lower() in e.place.lower())]
        asked = words(" ".join(terms))
        # A question of nothing but stopwords asks nothing, and ranked as no
        # question at all it would list the whole record as the answer.
        hits = _rank(entries, asked) if asked or not terms else []
        if floor:
            hits = [(share, e) for share, e in hits if share >= floor]

    # A working set is read whole by default: a card costs a few lines, and a
    # neighbour cut off onto a second page is one nobody turns to.
    limit = limit or (len(hits) if near else 10)
    start = (page - 1) * limit
    shown = hits[start:start + limit]
    if not hits:
        print("nothing here")
    else:
        best = hits[0][0]
        showing = (f"showing {start + 1}-{start + len(shown)}" if shown
                   else f"and page {page} is past the last")
        say = f"{len(hits)} found, {showing}"
        if near:
            say = f"{near} and {len(hits) - 1} a link away, {showing}"
        # A page number nobody was told about is a page nobody turns to, and
        # what was cut off then reads as everything there is.
        if start + len(shown) < len(hits):
            say += f" - the rest with --page {page + 1} or --limit {len(hits)}"
        if terms and not near:
            say += f"; the best answers {best:.0%} of that question"
            if best < THIN:
                say += " - the record may simply be silent on it"
        print(say)
    if near and not full and not show:
        _cards(entries, near, [entry for _, entry in shown])
        shown = []
    for score, entry in shown:
        if show:
            print(f"\n{entry}")
            for key in show:
                # `title` and `place` are the entry itself rather than fields
                # of it, and a column asking for one should not come back blank.
                print(f"    {key}: {getattr(entry, key, None) or entry.fields.get(key, '')}")
        elif full or near:
            _whole(entry)
        else:
            print(f"  {score:4.0%}  {entry.scanned(20)}   [{entry.place}]")
    if near:
        further = _a_step_further(entries, near)
        if further:
            print(
                f"\nwhat somebody else's software does, one link past that working "
                f"set ({len(further)}). Read one before trusting a behaviour it is about:"
            )
            for count, entry in further:
                print(f"  {count} x  {entry.scanned(8)}   [{entry.place}]")
    if terms and not near:
        for where, line, text in _in_source(words(" ".join(terms)), 3):
            print(f"  {where}:{line}  {text.strip()[:90]}")


def _whole(entry: Entry) -> None:
    print(f"\n=== {entry}   [{entry.place}]  {entry.path.relative_to(REPO)}")
    for key, value in entry.fields.items():
        print(f"    {key}: {value}")
    print(entry.body.strip())


#: The groups a working set is read in, and the order: the roads already put
#: down first, because working without them is how a rejected design comes back
#: proposed with confidence; then what is open beside the task; then the
#: reference; then what was finished.
GROUPS = (("put down", ("moot", "refused")),
          ("open", ("noted", "analyzed", "scoped")),
          ("known", ()),
          ("finished", ("done",)))


def _group(entry: Entry) -> int:
    if entry.known:
        return 2
    return next(n for n, (_, places) in enumerate(GROUPS) if entry.place in places)


def _decides(entry: Entry) -> str:
    """The one field that says whether a neighbour is worth opening.

    What a road put down rested on is its `because`, and a closed piece of work
    is its `outcome`; open work is its `criterion`, and a decision its
    `because`. A fact, a rule and a caught thought carry it in the title, which
    the card already shows.
    """
    if entry.place == "done":
        name = "outcome"
    elif entry.place in ("moot", "refused") or entry.kind == "decision":
        name = "because"
    elif not entry.known:
        name = "criterion"
    else:
        return ""
    # A citation of a name is read on the card by the name. The path is what
    # `check` and `stale` need and the name is what a reader deciding needs, a
    # test here being named for the claim it holds. A path naming nothing inside
    # it is left whole, the checkout being part of what it says.
    value = PATH.sub(lambda hit: hit.group().rsplit("::", 1)[-1] if "::" in hit.group()
                     else hit.group(), entry.fields.get(name, ""))
    return f"{name}: {value}" if value else ""


def _citing(entry: Entry, identity: str, ids: set[str], room: int) -> str:
    """The sentence of ``entry`` that cites ``identity``, where its prose does,
    cut to ``room`` characters about the citation.

    A neighbour reached through its own prose lit up for what that sentence
    says, and no field of it says the same. A citation of a split or merged
    entry counts as it does for `check`. A caught thought names entries bare as
    often as bracketed, so a bare identity is taken where no bracketed one is -
    where it carries a letter, since `10` is also a number.
    """
    prose = " ".join(entry.body.split())
    hits = [hit.start() for hit in REFERENCE.finditer(prose)
            if identity in _resolved(hit.group(1), ids)]
    at = hits[0] if hits else -1
    if at < 0 and _mixed(identity):
        # Not `1A` inside `1A.2`, which is another entry; a full stop ending
        # the sentence is punctuation.
        bare = re.search(rf"(?<![\w.]){re.escape(identity)}(?!\w|\.\w)", prose)
        at = bare.start() if bare else -1
    if at < 0:
        return ""
    start = prose.rfind(". ", 0, at) + 2 if prose.rfind(". ", 0, at) >= 0 else 0
    end = prose.find(". ", at)
    sentence = prose[start: end + 1 if end >= 0 else len(prose)].strip()
    # A long sentence is cut about the citation, so what is quoted shows it.
    inside = at - start - (len(prose[start:at]) - len(prose[start:at].lstrip()))
    if len(sentence) > room and inside > room // 3:
        sentence = "… " + sentence[inside - room // 3:].lstrip()
    return sentence


def _why(by_id: dict[str, Entry], identity: str, other: str) -> str:
    """Which way the link between two entries runs."""
    ids = set(by_id)
    here, there = _cites(by_id[identity], other, ids), _cites(by_id[other], identity, ids)
    return "both ways" if here and there else "cited here" if here else "cites this"


def _cards(entries: list[Entry], identity: str, shown: list[Entry]) -> None:
    """The entry in hand whole, and each neighbour as a card.

    Printed whole, a working set is thousands of words, most of them about
    entries that bear on the task through one sentence. A card says where the
    neighbour stands, which way the link runs, and the field that decides
    whether to open it - so a neighbour that lit up says why, and the second
    call is made on a reason rather than on the chance that something is in it.
    """
    by_id = {e.id: e for e in entries}
    room = max(shutil.get_terminal_size(fallback=(100, 24)).columns - 8, 40)
    heading = None
    for entry in shown:
        if entry.id == identity:
            _whole(entry)
            continue
        group = GROUPS[_group(entry)][0]
        if group != heading:
            print(f"\n{group}:")
            heading = group
        print(f"  {entry.id:<5} [{entry.place}]  {_why(by_id, identity, entry.id)}")
        cites = _citing(entry, identity, set(by_id), room * 2 - 2)
        for text, lines in ((entry.title, 2), (cites and f"> {cites}", 2),
                            (_decides(entry), 3)):
            if text:
                print(textwrap.fill(text, room + 8, max_lines=lines, placeholder=" …",
                                    initial_indent=" " * 8, subsequent_indent=" " * 8,
                                    break_long_words=False, break_on_hyphens=False))
    if any(entry.id != identity for entry in shown):
        print("\nkb find --near <id> opens one; --full prints every one whole")


def _named(entry: Entry) -> set[str]:
    """Every identity an entry cites: its `related`, and a `[[id]]` anywhere."""
    cited = set(_list(entry.fields.get("related", "")))
    for text in (entry.body, *entry.fields.values()):
        cited |= set(REFERENCE.findall(text))
    return cited


def _resolved(cited: str, ids: set[str]) -> set[str]:
    """The entries a citation reaches, by the rule `resolves` checks it by: the
    entry itself, else the parts it was split into, else what it was merged
    back into."""
    if cited in ids:
        return {cited}
    parts = {i for i in ids if i.startswith(cited + ".")}
    while not parts and "." in cited:
        cited = cited.rsplit(".", 1)[0]
        parts = {cited} & ids
    return parts


def _cites(entry: Entry, identity: str, ids: set[str]) -> bool:
    return any(identity in _resolved(cited, ids) for cited in _named(entry))


def _linked(entries: list[Entry], identity: str) -> set[str]:
    """Every entry one link from this one, in either direction."""
    by_id = {e.id: e for e in entries}
    ids = set(by_id)
    near: set[str] = set()
    if identity in by_id:
        for cited in _named(by_id[identity]):
            near |= _resolved(cited, ids)
    near |= {entry.id for entry in entries if _cites(entry, identity, ids)}
    return near - {identity}


def _around(entries: list[Entry], identity: str) -> list[Entry]:
    """An entry and everything one link away - the working set for a task."""
    by_id = {e.id: e for e in entries}
    if identity not in by_id:
        sys.exit(f"no entry {identity}")
    around = sorted((by_id[i] for i in _linked(entries, identity)),
                    key=lambda entry: (_group(entry), entry.id))
    return [by_id[identity], *around]


def _a_step_further(entries: list[Entry], identity: str) -> list[tuple[int, Entry]]:
    """What somebody else's software does, one link past the working set.

    The working set is what an entry names and what names it, and that is the
    right size to read. What it misses is the entry nobody thought to link: a
    measurement of a client's or an engine's behaviour that bears on the task
    through a *neighbour* rather than through the task itself. The linking is
    done by hand, and a fact written today does not walk back into the entries
    it bears on.

    So the second link is offered, and **only for `THEIRS`**. A whole second hop
    is a hundred entries and reads as noise; cut to what we do not control it is
    a handful, and it is the handful that matters, because the failure it exists
    to prevent is depending on a behaviour somebody already measured and wrote
    down. Ranked by how much of the working set reaches each, since an entry
    several of them touch is more likely to bear on the task than one reached
    down a single thread.
    """
    by_id = {e.id: e for e in entries}
    inner = _linked(entries, identity)
    reach: dict[str, int] = {}
    for near in inner:
        for beyond in _linked(entries, near):
            if beyond not in inner and beyond != identity:
                reach[beyond] = reach.get(beyond, 0) + 1
    found = [(count, by_id[i]) for i, count in reach.items() if by_id[i].place in THEIRS]
    return sorted(found, key=lambda pair: (-pair[0], pair[1].id))


# ---------------------------------------------------------------- the record

#: Shown as marks beside every entry already, so offering one as a cut says
#: nothing the reader is not looking at.
MARKED = ("release", "quiet", "needs-human")


def _commonest_subject(entries: list[Entry]) -> str:
    """The tag most of a list shares, so a hint offers a cut that exists."""
    counted: dict[str, int] = {}
    for entry in entries:
        for tag in entry.tags:
            if tag not in MARKED:
                counted[tag] = counted.get(tag, 0) + 1
    return max(sorted(counted), key=lambda tag: counted[tag], default="")


def state(entries: list[Entry], faults: list[str], limit: int = 12) -> None:
    at = {place: [e for e in entries if e.place == place] for place in QUEUE}

    def show(entry: Entry, marks: str = "") -> None:
        print(f"  {marks:>3} {entry.scanned(6)}")
        detail = entry.fields.get("criterion") or entry.fields.get("because")
        if detail:
            print(f"           {detail}")

    def mark(entry: Entry) -> str:
        return ("*" if "release" in entry.tags else "") \
             + ("!" if "quiet" in entry.tags else "") \
             + ("?" if "needs-human" in entry.tags else "")

    def rank(entry: Entry) -> int:
        """Quiet first, since nothing new is meant to land while one is open,
        then what a release waits on, then what waits on a person."""
        order = ("quiet", "release", "needs-human")
        return min((order.index(tag) for tag in entry.tags if tag in order), default=len(order))

    # Said once, on the first heading whose rows carry a mark, so a queue with
    # nothing ready to pick up still explains the marks in the one below it.
    legend = ["   * release   ! can be wrong quietly   ? wants a human"]

    def heading(title: str, rows: list[Entry]) -> str:
        return title + (legend.pop() if legend and any(map(mark, rows)) else "")

    for place, title in (("scoped", "in scope"), ("analyzed", "ready to pick up")):
        if not at[place]:
            continue
        rows = sorted(at[place], key=lambda e: (rank(e), e.id))
        print(heading(f"{title} ({len(rows)})", rows[:limit]))
        for entry in rows[:limit]:
            show(entry, mark(entry))
        if len(rows) > limit:
            subject = _commonest_subject(rows)
            print(f"       … {len(rows) - limit} more - kb find --field place={place}"
                  + (f", and any tag narrows it: --field tags={subject}" if subject else ""))
        print()

    topics: dict[str, int] = {}
    for entry in (e for e in entries if e.known):
        topics[entry.place] = topics.get(entry.place, 0) + 1
    print("known: " + ", ".join(f"{v} {k}" for k, v in sorted(topics.items())))
    def kinds(value: str) -> list[str]:
        # Every kind the field carries, not its first word: a fact found by a
        # measurement and held by a test since re-runs, whatever came first.
        return list(dict.fromkeys(kind for kind, _ in _evidence(value))) or ["?"]

    weak = [e for e in entries
            if (e.known and e.kind == "fact"
                and not set(kinds(e.fields.get("provenance", ""))) & set(RERUN))
            or (e.place == "done"
                and not set(kinds(e.fields.get("outcome", ""))) & set(RERUN))]
    for entry in weak[:limit]:
        field = entry.fields.get("provenance") or entry.fields.get("outcome", "")
        print(f"     rests on {', '.join(kinds(field))}: {entry}")
    if len(weak) > limit:
        print(f"     … {len(weak) - limit} more")

    if at["noted"]:
        # A marked entry is caught as often as it is shaped, and oldest first
        # would bury a new one under a hundred older thoughts.
        rows = sorted(at["noted"], key=lambda e: (rank(e), e.fields.get("noted", "")))
        print(heading(f"\ncaught, not yet shaped ({len(rows)})", rows[:limit]))
        for entry in rows[:limit]:
            print(f"  {mark(entry):>3} {entry.scanned(20)}   [{entry.fields.get('noted', '?')}]")
        if len(rows) > limit:
            print(f"      … {len(rows) - limit} more, the marked first and then oldest first")

    print(f"\nfinished: {len(at['done'])} done, {len(at['moot'])} moot, "
          f"{len(at['refused'])} refused")
    said = "walkable" if not faults else f"{len(faults)} faults - run check"
    overgrown = grown(entries)
    if overgrown:
        # Said here because this is what a session reads first, and a prompt
        # printed only where `check` runs is one nobody sees.
        said += f"; {len(overgrown)} grown past their body - kb check lists them"
    unshaped = worked_unshaped(entries)
    if unshaped:
        said += (f"; {len(unshaped)} worked on while still caught, with no criterion"
                 " - kb check lists them")
    print(f"record: {said}")


def check(entries: list[Entry], broken: list[str]) -> list[str]:
    """Whether the record can still be walked. Never whether it says anything.

    Every rule asks whether something is *there* - a field, a file, a target.
    None reads what a field says, and none ever will: `criterion: fix it`
    passes. Content is the reader's business, and that separation is the
    design rather than a shortfall of it.
    """
    faults, seen = list(broken), {}

    for entry in entries:
        at = entry.path.relative_to(ROOT)
        if entry.id in seen:
            faults.append(f"{at}: {entry.id} is already {seen[entry.id].path.relative_to(ROOT)}")
        seen[entry.id] = entry

        faults += _held(entry, entries)

    # The documents a reader is sent to for what is true now. `load` walks the
    # entries and nothing walks these, so a citation in one of them was held to
    # nothing at all - and they are where somebody looks first.
    for name in DOCUMENTS:
        start = REPO / name
        pages = [start] if start.is_file() else sorted(start.rglob("*.md"))
        for page in (page for page in pages if page.is_file()):
            at = page.relative_to(REPO)
            prose = _prose(page.read_text(encoding="utf-8", errors="replace"))
            faults += _unreachable(at, prose)
            faults += _cited(at, prose, names_only=True)

    identities = set(seen)
    for entry in entries:
        for cited in _list(entry.fields.get("related", "")):
            if not resolves(cited, identities):
                faults.append(f"{entry.path.relative_to(ROOT)}: related {cited} leads nowhere")
    for cited, page in _citations():
        if IDENTITY.match(cited) and not resolves(cited, identities):
            faults.append(f"{page}: [[{cited}]] leads nowhere")

    return faults


def _held(entry: Entry, entries: list[Entry]) -> list[str]:
    """What one entry breaks of what its place asks of it.

    Asked by `check` of every entry where it stands, and by `close` of an entry
    where it is about to stand - one set of rules, so the tool cannot move a
    file into a place that `check` then refuses it in.
    """
    at = entry.path.relative_to(ROOT)
    faults: list[str] = []

    # A citation is a claim about the source wherever it stands, so it is
    # asked before the place is: `noted/` is where an entry sits longest,
    # and is the one place nothing else here holds to anything. Every
    # field, because a criterion naming the population it is checked over
    # carries one as readily as a provenance does. `related` holds
    # identities rather than paths, and is resolved in `check`.
    prose = _prose(entry.body)
    for name, value in entry.fields.items():
        if name != "related":
            faults += _unreachable(at, value) + _cited(at, value)
    # The title and the body are one sentence written on one day - `note`
    # takes the first from the second - so they are read together, and a
    # closed entry's are held the way `moved_under` says. Its other fields
    # are evidence and fail whatever the place, that being what a reader is
    # sent to.
    faults += _unreachable(at, entry.title) + _unreachable(at, prose)
    if entry.known or entry.place not in TERMINAL:
        faults += _cited(at, entry.title, names_only=True)
        faults += _cited(at, prose, names_only=True)

    # Everything below is what a place promises about its fields, and
    # `noted/` promises nothing: a thought is caught as one string.
    if entry.place == "noted":
        return faults

    if entry.kind not in KINDS:
        faults.append(f"{at}: kind {entry.kind!r} is not one of {list(KINDS)}")
    faults += _wanting(entry, entries)
    if entry.kind == "fact" and entry.fields.get("provenance"):
        faults += _provenance(at, entry.fields["provenance"])

    if entry.place in TERMINAL:
        if not entry.fields.get("closed"):
            faults.append(f"{at}: {entry.place} with no date")
        wanted = "outcome" if entry.place == "done" else "because"
        if not entry.fields.get(wanted):
            faults.append(f"{at}: {entry.place} with no {wanted}")
        elif entry.place == "done":
            faults += _provenance(at, entry.fields["outcome"])
        if "quiet" in entry.tags:
            faults.append(f"{at}: quiet on a {entry.place} entry - the mark says a "
                          f"wrong number can still come back, and the query that "
                          f"gathers them does not filter by place")

    working = entry.fields.get("working", "")
    try:
        archived = bool(working) and (ARCHIVE / Path(working).name).exists()
    except OSError:  # a name the file system cannot hold names nothing there
        archived = False
    if working and not archived:
        faults.append(f"{at}: working names {working}, which is not in kb/archive/")
    return faults


def _wanting(entry: Entry, entries: list[Entry]) -> list[str]:
    """The fields an entry's kind and tags ask for that it does not carry.

    Each is mended by writing a field, and nothing else in `_held` is: the rest
    are about what a value says. `set` lets a write open one of these where it
    mends another, which is how `kind` gets written before the field it asks
    for.
    """
    at = entry.path.relative_to(ROOT)
    faults = []
    if entry.kind == "work" and not entry.fields.get("criterion"):
        faults.append(f"{at}: work with nothing that would show it done")
    if entry.kind == "decision" and not entry.fields.get("because"):
        faults.append(f"{at}: a decision with no reasoning to fail")
    if entry.kind == "fact" and not entry.fields.get("provenance"):
        faults += _provenance(at, "")
    if "measurement" in entry.tags and not _defends(entry, entries):
        faults.append(f"{at}: a measurement defending no stated number - "
                      f"relate it to something in known/status/")
    return faults


#: The dated notes a shaped entry carries before its body is out of date. A
#: closed entry ordinarily takes two after it closes - what the adversarial
#: tester found and what the review taught - and a third is the body being
#: overtaken rather than added to.
GROWN = 2

#: A line `note` appends: the date in italics, a dash, the sentence.
DATED = re.compile(r"^\*\d{4}-\d{2}-\d{2}\* - ", re.MULTILINE)


def grown(entries: list[Entry]) -> list[tuple[int, Entry]]:
    """Shaped entries that have grown by dated notes past their body.

    A note is how a thought is caught while working, and the body is what the
    entry says is true. Once the notes outnumber what a body takes in the
    ordinary run of closing, a reader has to replay them to learn which of the
    body's sentences still stand, and every `find --near` that reaches the
    entry hands that replay to its reader. That is debt, paid by rewriting the
    body to what is true now and moving the notes to `kb/archive/` under
    `working:`.

    A **prompt and not a fault**, as `worked_through` is: an entry in scope
    gathers notes as the working log, and grooming it is judgement. `noted/` is
    left out, being a scratchpad by design until somebody shapes it.
    """
    counted = [(len(DATED.findall(entry.body)), entry)
               for entry in entries if entry.place != "noted"]
    return sorted(((n, e) for n, e in counted if n > GROWN), key=lambda pair: pair[1].id)


def worked_unshaped(entries: list[Entry]) -> list[tuple[int, Entry]]:
    """Caught thoughts that have gathered notes past what catching one takes.

    A thought is caught in a line and added to once or twice while it is still
    a thought. An entry in `noted/` whose notes run past :data:`GROWN` is being
    worked - measured, argued, built against - with no criterion to finish it
    by, and nothing in the directory says so: `noted/` is where nothing is
    promised, so the work is invisible to anybody reading what is in scope. The
    way out is to shape it - write the criterion, rewrite the body, move it to
    `scoped/` - or to split off the thought it started as.

    A **prompt and not a fault**, as :func:`grown` is.
    """
    counted = [(len(DATED.findall(entry.body)), entry)
               for entry in entries if entry.place == "noted"]
    return sorted(((n, e) for n, e in counted if n > GROWN), key=lambda pair: pair[1].id)


def worked_through(entries: list[Entry]) -> list[Entry]:
    """Entries that have been finished and have not moved.

    Closing is written before the file is moved - by hand the two are one act,
    and putting the demand there is what gets an outcome written while the
    answer is still in somebody's head. The cost of that order is a window: an
    entry can carry everything a terminal place asks for and still be sitting in
    the queue, which is a thing nobody looking at the directory can see.

    So this is a **prompt and not a fault**. There are good reasons to hold one
    open - a second reader who has not been through it yet, a tier that has not
    been run - and the entry's own prose is where they belong. What there is no
    good reason for is nobody noticing.
    """
    return sorted(
        (
            entry
            for entry in entries
            if entry.place not in TERMINAL
            and any(entry.fields.get(field) for field in ("outcome", "closed"))
        ),
        key=lambda entry: entry.id,
    )


def moved_under(entries: list[Entry]) -> list[str]:
    """Where a closed entry's title or prose names what its file no longer defines.

    A **prompt and not a fault**, for the reason `worked_through` is one, and
    for a second reason of its own. A closed entry carries a date, and its body
    is what was true on that date: a function may sit in one file when one
    entry closes and in another when the next does, and both entries are right.
    Failing the run puts the reader under pressure to repoint the path, which is
    backdating - and where the entry's own work replaced what it diagnosed,
    repointing writes a false statement about today's code in the record's
    strongest form.

    So the run says which closed entries the code has moved under, and the
    reader decides one at a time: the path where the sentence survives the
    move, and the name written as ordinary prose where it does not.

    A field is held the other way and fails, closed or not. An `outcome` is
    evidence a reader is meant to reach, and `stale` runs it.
    """
    return [
        fault
        for entry in entries
        if entry.place in TERMINAL and not entry.known
        for fault in _cited(entry.path.relative_to(ROOT), entry.title, names_only=True)
        + _cited(entry.path.relative_to(ROOT), _prose(entry.body), names_only=True)
    ]


def _defends(entry: Entry, entries: list[Entry]) -> bool:
    """The rule that bounds the queue: measuring can always be done more finely,
    and the only thing that says when to stop is a number somebody claims."""
    claimed = {e.id for e in entries if e.place == "status"}
    return any(resolves(cited, claimed) for cited in _list(entry.fields.get("related", "")))


def _provenance(at: Path, value: str) -> list[str]:
    if not value:
        return [f"{at}: nothing said about where this is re-derived"]
    kind = value.split(":", 1)[0].strip()
    if kind not in PROVENANCE:
        return [
            f"{at}: {kind!r} is not one of {list(PROVENANCE)} - the field carries"
            f" evidence, not a summary, and {HERE / 'schema.md'} says what each kind is"
        ]
    return []


def _prose(body: str) -> str:
    """A body with its fenced blocks blanked, every other offset kept.

    Blanked rather than cut, because the citation rules below read one span
    against another and a cut would slide them past each other.
    """
    return FENCE.sub(lambda hit: re.sub(r"[^\n]", " ", hit.group()), body)


def _unreachable(at: Path, text: str) -> list[str]:
    """Citations naming something inside a file that no path reaches.

    `PATH` is rooted at the trees the project owns, so `header.go::unfold`, a
    package-relative `part/tree.go::Walk` and a bare `::unfold` carrying on from
    the sentence before are resolved by nothing here. The form claims the file
    defines the name and nothing asks the file, which is the emptiest thing in
    the record wearing the strongest form.

    Held the same way in a body as in a field. A basename resolves today because
    one file happens to carry it, and the day a second one is added every
    citation written that way turns ambiguous at once, in a change that touched
    none of them. A reader has the same problem: a tree easily holds a
    `specification.md` under several `doc/` directories.
    """
    reached = [hit.span() for hit in PATH.finditer(text)]
    faults = [
        f"{at}: cites {hit.group()!r}, which no path reaches - name the file "
        f"from the repository root, in a tree {PROJECT} lists as owned, or "
        "nothing here runs it"
        for hit in NODE.finditer(text)
        if not any(start <= hit.start() < end for start, end in reached)
    ]
    # A path this tool resolves, with a `::` left hanging off it. `PATH` ends on
    # a word character, so it backtracks off the colons and reports a file that
    # is there while the name goes unread - and the way to write one is to wrap
    # a long citation, which this record does to every field it carries on an
    # indented line.
    faults += [
        f"{at}: cites {hit.group()!r} and then breaks before the name - "
        "a citation is written on one line or nothing reads the name"
        for hit in PATH.finditer(text)
        if text[hit.end() : hit.end() + 2] == "::"
    ]
    return faults


def _cited(at: Path, text: str, names_only: bool = False) -> list[str]:
    """Every path ``text`` names, still there - and what it names inside one, still defined in it.

    A **name** is the exact half of the question a citation raises.
    `src/header.go::Field.unfold` is written in that file or it is
    not, where a bare path only says the file still exists - so a claim written
    with the name in it is one this can answer, and one written in prose beside
    it is not.

    ``names_only`` is how prose is read, and evidence is read the other way.
    Where a field carries a citation, the file is the claim and a missing one is
    a fault. A body is English, and the record's own subject includes things
    that have been **deleted** - so prose is held to the name alone, and a file
    that has gone takes the sentence about it with it rather than failing.

    A tree that is not checked out says nothing either way, so its citations are
    passed over rather than failed: the repositories are released on their own
    cadence and cloned on their own, and a reader without one is not holding a
    stale record.
    """
    faults = []
    for cited in PATH.findall(text):
        page, _, node = cited.partition("::")
        page = LINES.sub("", page)          # `picks.py:82` is a line, not a path
        if names_only and not node:
            continue
        if _away(page):
            continue
        target = REPO / page
        if not target.exists():
            if not names_only:
                faults.append(f"{at}: names {page}, which is not there")
        elif node and not target.is_file():
            faults.append(f"{at}: names {node} inside {page}, which is a directory")
        elif node:
            # Asked whole rather than a name at a time: a class and a test both
            # existing somewhere in the file is what pytest refuses to collect,
            # and it is the shape a rename leaves behind.
            body = target.read_text(encoding="utf-8", errors="replace")
            if not _defined(node, page, body):
                faults.append(f"{at}: names {node}, which {page} does not define")
    return faults


def _away(page: str) -> bool:
    """Whether a cited path is in a tree the working copy may be without, and is."""
    tree = page.split("/")[0]
    return tree in OUTSIDE and not (REPO / tree).exists()


def _defined(name: str, page: str, body: str) -> bool:
    """Whether ``page`` is where ``name`` is written down, not merely a file
    that mentions it.

    A citation is only worth its form if it fails when the thing moves. Asked as
    a word anywhere in the text, it holds on the file that names its new home in
    a doc comment - which is exactly what a module does the day a function
    leaves it, so the citation survives the one event it exists to catch.

    A name written `Class::method` or `Class.method` is asked as what it says:
    each is defined inside the one before it. Asked as independent names it
    would pass on a file holding both in different classes, which is the case
    pytest refuses to collect - and that form is what every `outcome` and
    `provenance` in the record is written in, so a crossed pair here is a fact
    validated by running a different test.

    Python is **parsed**: a definition at column zero matches inside a
    triple-quoted fixture, a definition indented matches a local inside a
    function, and `REFINE, COARSEN = ...` binds two names that no pattern of the
    form `^name =` reaches. Go is read by pattern, because `gofmt` puts every
    top-level declaration at column zero and a doc comment naming a function is
    `// name`, never `func name` - see :func:`_go_defined`. Anything else is
    held to the word, there being no definition to look for.
    """
    if page.endswith(".py"):
        return _inside(re.split(r"::|\.", name), body)
    if page.endswith(".go"):
        return _go_defined(re.split(r"::|\.", name), body)
    return bool(re.search(rf"\b{re.escape(name)}\b", body))


def _bound(node: ast.AST) -> list[str]:
    """Names a statement binds where it stands, ignoring what it binds them to."""
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return [node.name]
    targets: list[ast.expr] = []
    if isinstance(node, ast.Assign):
        targets = list(node.targets)
    elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        targets = [node.target]
    found = []
    while targets:
        target = targets.pop()
        if isinstance(target, ast.Name):
            found.append(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            targets += list(target.elts)
    return found


def _scope(node: ast.AST) -> list[ast.AST]:
    """The statements written in this scope, reaching through the branches.

    A `class` under a module-level `if TYPE_CHECKING` or inside a `try` is
    written in that module, and a reader citing it means that file. A `def`
    inside another `def` is not: it is a local, and nothing outside can reach
    it, so the walk stops at anything that opens a scope of its own.
    """
    written = []
    for child in ast.iter_child_nodes(node):
        written.append(child)
        if isinstance(child, (ast.If, ast.Try, ast.With, ast.For, ast.While)):
            written += _scope(child)
    return written


def _inside(path: list[str], body: str) -> bool:
    """Whether ``body`` nests these definitions one in the next, outermost first.

    One name on its own is the exception and is looked for in the module and in
    each class in it, because that is the form most of the record uses for a
    test and `stale` resolves it the same way - it is a claim that the file
    holds the name, and nothing about where.

    A file this interpreter cannot parse is held to the word, as a file in any
    other language is: it may be written for a newer Python than the one
    running the tool, and answering no would report every name in it gone.
    """
    try:
        tree = ast.parse(body)
    except (SyntaxError, ValueError):
        # ValueError: a NUL byte, before Python 3.12 made it a SyntaxError.
        return all(re.search(rf"\b{re.escape(name)}\b", body) for name in path)
    if len(path) == 1:
        scopes = [tree] + [node for node in _scope(tree) if isinstance(node, ast.ClassDef)]
        return any(path[0] in _bound(node) for scope in scopes for node in _scope(scope))
    scope: ast.AST = tree
    for name in path:
        found = [node for node in _scope(scope) if name in _bound(node)]
        if not found:
            return False
        if not isinstance(found[0], (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            return name == path[-1]
        scope = found[0]
    return True


#: Where Go writes a top-level declaration down: a function, generic or not; a
#: method on any receiver; a type; a single var or const. `{n}` is the name.
GO_DECLARED = (
    r"^func\s+{n}\s*[(\[]",
    r"^func\s*\([^)]*\)\s*{n}\s*[(\[]",
    r"^type\s+{n}\b",
    r"^(?:var|const)\s+{n}\b",
)
#: The grouped form of the last two and of `type`, whose members stand indented
#: on their own lines between the parentheses.
GO_GROUP = re.compile(r"^(?:var|const|type)\s*\(\n(.*?)^\)", re.MULTILINE | re.DOTALL)
#: The type parameters a generic type declares and its receivers carry, where
#: there are any. Lazy, so that a constraint with brackets of its own -
#: `~[]byte` - takes it only as far as what follows it needs.
GO_PARAMS = r"(?:\[.*?\])?"
#: A struct's fields or an interface's methods, one to a line inside the braces.
GO_MEMBERS = r"^type\s+{n}" + GO_PARAMS + r"\s+(?:struct|interface)\s*\{{\n(.*?)^\}}"
#: A method on the type `{n}` named `{m}`, whatever the receiver is called.
GO_METHOD = r"^func\s*\([^)]*\b{n}" + GO_PARAMS + r"\s*\)\s*{m}\s*[(\[]"


def _go_defined(path: list[str], body: str) -> bool:
    """Whether a Go file declares ``path``, outermost first.

    The first name has to be declared at the top level, alone or in a group. A
    second name after a type is a method on it or a member of it; after a
    function it is a subtest, which Go declares nowhere - `t.Run` takes a
    string - so what follows a function is held to the word. Anything deeper
    is held to the word as well, there being nothing in Go that nests further.

    A method is the exception to the first rule. Go lets it sit in any file of
    its type's package, so `Type.Method` claims the method and not the type,
    and the file it names is the one writing the func, wherever the type is
    declared. A member has no such freedom: it is written where its type is.

    A pattern is honest here where Python needed a parser, because the
    language's own formatter puts every top-level declaration at column zero
    and nothing else there: a doc comment naming a function's new home is
    `// name`, and a raw string quoting a declaration sits inside whatever
    holds it. A file that is nothing but such a string would fool it, and no
    test file here is one.
    """
    first, rest = path[0], path[1:]
    n = re.escape(first)
    if rest and re.search(GO_METHOD.format(n=n, m=re.escape(rest[0])), body, re.MULTILINE):
        return all(re.search(rf"\b{re.escape(part)}\b", body) for part in rest[1:])
    groups = GO_GROUP.findall(body)
    declared = any(re.search(p.format(n=n), body, re.MULTILINE) for p in GO_DECLARED) \
        or any(re.search(rf"^\s+{n}\b", group, re.MULTILINE) for group in groups)
    if not declared:
        return False
    if not rest:
        return True
    a_type = re.search(rf"^type\s+{n}\b", body, re.MULTILINE) \
        or any(re.search(rf"^\s+{n}\s+\S", group, re.MULTILINE)
               for group in re.findall(r"^type\s*\(\n(.*?)^\)", body, re.MULTILINE | re.DOTALL))
    if a_type:
        members = re.search(GO_MEMBERS.format(n=n), body, re.MULTILINE | re.DOTALL)
        if not (members and re.search(rf"^\s+{re.escape(rest[0])}\b", members.group(1),
                                      re.MULTILINE)):
            return False
        rest = rest[1:]
    return all(re.search(rf"\b{re.escape(part)}\b", body) for part in rest)


def _citations() -> list[tuple[str, str]]:
    found = []
    for name in CITERS:
        start = REPO / name
        if not start.exists():
            continue
        for page in ([start] if start.is_file() else sorted(start.rglob("*.md"))):
            for cited in REFERENCE.findall(page.read_text(encoding="utf-8", errors="replace")):
                found.append((cited, str(page.relative_to(REPO))))
    return found


# -------------------------------------------------------------------- stale

def dry(entries: list[Entry]) -> int:
    """What `stale` would run, and what it could never run - without running it.

    The second half is the useful one and costs nothing: a claim whose evidence
    is prose carries no citation to go red, so it is invisible to every check
    here and reads as settled. Listing those is how a constant bracketed by two
    runs nobody can repeat gets found.

    The third list is a **reading list and not a verdict** - entries stating a
    figure with nothing cited that re-derives it. A nominal rating and a
    filename suffix land in it beside a real one; deciding which is which is the
    reader's, as everywhere else here.
    """
    runs, prose, figures = [], [], []
    for entry in entries:
        rerun = False
        for field in ("provenance", "outcome"):
            value = entry.fields.get(field, "")
            if not value:
                continue
            carried = _evidence(value)
            rerun = rerun or any(kind in RERUN for kind, _ in carried)
            for kind, text in carried:
                if kind == "test":
                    runs += [(entry, cited) for cited in PATH.findall(text)]
            if not any(kind == "test" for kind, _ in carried) and not PATH.search(value) \
                    and entry.known:
                prose.append((carried[0][0], entry))
        held = FIGURE.findall(entry.body)
        if held and not rerun:
            figures.append((entry, sorted(set(held))[:4]))

    unknown = 0
    mentioned = 0
    if runs and not RUNNERS:
        print(f"{_no_runners()}\n")
    away = 0
    for entry, cited in runs:
        page = cited.partition("::")[0]
        runner = _runner(page)
        if _away(page):
            away += 1
            print(f"not here    {entry.id:<5} {'-':<15} {cited}")
        elif runner is not None:
            print(f"would run   {entry.id:<5} {'run/' + runner:<15} {cited}")
        elif not RUNNERS or _test_by_line(page):
            unknown += 1
            print(f"no command  {entry.id:<5} {'-':<15} {cited}")
        else:
            mentioned += 1
            print(f"mentioned   {entry.id:<5} {'-':<15} {cited}")
    for kind, entry in prose:
        print(f"no citation {kind:9} {entry}")
    for entry, held in figures:
        print(f"figure      {entry}\n            {', '.join(held)}")
    print(f"\n{len(runs) - unknown - mentioned - away} would be run; {unknown} cited under test: "
          f"are no test a command here runs; {mentioned} under test: are mentioned beside "
          f"a test and run by nothing; {len(prose)} rest on prose and can never go red; "
          f"{len(figures)} state a figure nothing here re-derives"
          + (f"; {away} in a tree that is not here" if away else ""))
    return 0


def rules(entries: list[Entry]) -> int:
    """Every guideline, in one screen.

    A rule you have to remember to look up does not fire: you do not know to
    search for *do not trust that number* until after you have trusted it. So
    the whole set is one command, cheap enough to run at the start of a session,
    and each title is written to carry its rule on its own. The entry behind it
    carries the mechanism and the occasion that taught it.
    """
    held = sorted((e for e in entries if e.place == GUIDELINES), key=lambda e: e.id)
    for entry in held:
        print(f"  {entry}")
    print(f"\n{len(held)} of them. `kb find --near <id>` for the one that bites,"
          f"\nand {HERE / 'SKILL.md'} for the procedure they sit inside.")
    return 0


#: A line or a range written after a path, which addresses a file and no test.
LINE = re.compile(r":\d+(?:-\d+)?$")


def _runner(page: str) -> str | None:
    """The command under `run/` that owns a cited file, or None where none does."""
    name = Path(page).name
    return next((command for pattern, command in RUNNERS.items()
                 if fnmatch.fnmatchcase(name, pattern)), None)


def _test_by_line(page: str) -> bool:
    """Whether a path is a test file cited by a line, which runs no test and is
    meant to: the one path under `test:` no command owns that is not a mention."""
    return LINE.search(page) is not None and _runner(LINE.sub("", page)) is not None

#: The exit statuses a command reports its verdict with. Anything else is red.
GREEN, NOT_RUN = 0, 77


def _contract() -> str:
    """Where the record says what a command under `run/` must do: its own copy
    of the contract, which is what a reader of the record has to hand."""
    return str((ROOT / "run" / "README.md").relative_to(REPO))


def _no_runners() -> str:
    """Why nothing under `test:` ran in a record that names no runner."""
    return (f"{PROJECT} names no runners, so no command here runs a test - "
            f"see {_contract()}")


def _said(done: subprocess.CompletedProcess) -> str:
    """The last line a command printed, which the contract makes its reason."""
    lines = [line for line in done.stdout.strip().split("\n") if line.strip()]
    lines = lines or [line for line in done.stderr.strip().split("\n") if line.strip()]
    return lines[-1].strip() if lines else ""


def _command(name: str, held: dict[str, tuple[Path | None, str]]) -> tuple[Path | None, str]:
    """The record's command for a kind of test, asked once per run whether its
    toolchain is there and then held; or why there is none.

    How a test is run belongs to the project, so the tool asks the record rather
    than looking for an interpreter itself. `held` belongs to the run rather than
    to the module: a cache living longer than the call would answer a later run
    from an environment that has since changed.
    """
    if name in held:
        return held[name]
    command = ROOT / "run" / name
    if not (command.is_file() and os.access(command, os.X_OK)):
        found: tuple[Path | None, str] = (
            None, f"the record has no executable run/{name} - see {_contract()}")
    else:
        try:
            done = subprocess.run([str(command), "--probe"], cwd=REPO, capture_output=True,
                                  stdin=subprocess.DEVNULL, text=True, timeout=600)
        except (OSError, subprocess.TimeoutExpired) as error:
            found = None, f"run/{name} --probe did not answer: {error}"
        else:
            said = _said(done)
            found = (command, said) if done.returncode == 0 else \
                (None, f"run/{name} --probe: {said or 'it failed and said nothing'}")
    held[name] = found
    return found


def _run(command: Path, page: str, name: str) -> tuple[str, str]:
    """Run one citation through the record's command, and read its verdict off
    the exit status. A citation naming nothing inside the file hands on the path
    alone."""
    cited = f"{page}::{name}" if name else page
    try:
        # Nothing to read: a test asking for input would otherwise wait on
        # whatever `kb` was started with, until the clock ran out.
        done = subprocess.run([str(command), page, *([name] if name else [])], cwd=REPO,
                              capture_output=True, stdin=subprocess.DEVNULL, text=True,
                              timeout=600)
    except subprocess.TimeoutExpired:
        # One test outrunning the clock is a finding about that test, never a
        # reason to stop asking about the rest.
        return "red", f"{cited} did not finish inside the timeout"
    except OSError as error:
        return "red", f"run/{command.name} could not be started: {error}"
    said = _said(done) or f"run/{command.name} said nothing about {cited}"
    if done.returncode == GREEN:
        return "green", said
    if done.returncode == NOT_RUN:
        return "unrun", said
    return "red", said


def stale(entries: list[Entry]) -> int:
    """Which facts have lost their evidence, and which never had any that runs.

    A fact whose provenance is a test is only as good as that test still
    passing; nothing else here re-derives anything. So this runs them all and
    prints what went red beside what was never going to move.

    **It runs each cited test for real**, through the command the record keeps
    under `run/` for the kind of file the citation names, and the record's
    `runners` - :data:`RUNNERS` - is the whole of that. How a test is run
    belongs to the project, and the command's exit status is the verdict. A
    record naming no runner has every cited test counted as not run, said once:
    a run that ran nothing is not a record found clean. Neither command is assumed - run without one, every test it
    owned would go red saying so, and a line of real staleness would drown in a
    page of the same complaint. So a command that is not there, or whose probe
    says its toolchain is not, is reported **once**, by name, and the tests it
    owned are counted as not run rather than as anything.

    A skip is reported as *not run* rather than as green, because a test that
    did not execute is the absence of evidence and must not print like the
    presence of it. That is the command's to say, by exiting 77.

    A test in a tree named `outside` that this working copy is without is
    passed over and counted, as `check` passes over its citations.

    A path under `test:` whose name is no test's - the code a test covers, the
    helper it drives, a results file beside it - is a **mention**: run by
    nothing and failing nothing, because a sentence about a test names what the
    test exercises, and `check` holds those names already. `--dry-run` lists
    them. A test file cited by a line is **unknown**: it names a test and
    addresses none, so the record is unchecked there, and it fails the run the
    way a missing toolchain does.
    """
    red, skipped, mute, unknown = [], [], [], []
    mentioned = away = 0
    absent: dict[str, int] = {}
    held: dict[str, tuple[Path | None, str]] = {}
    for entry in entries:
        for field in ("provenance", "outcome"):
            value = entry.fields.get(field, "")
            if not value:
                continue
            carried = _evidence(value)
            tests = [text for kind, text in carried if kind == "test"]
            if not tests:
                # A gate runs on its own schedule, and the rest never re-run.
                if carried[0][0] in RERUN or entry.known:
                    mute.append((carried[0][0], entry))
                continue
            for cited in (cited for text in tests for cited in PATH.findall(text)):
                page, _, name = cited.partition("::")
                if _away(page):
                    # Passed over as `check` passes it: a tree not checked out
                    # says nothing about the record either way.
                    away += 1
                    continue
                if not RUNNERS:
                    why = _no_runners()
                    absent[why] = absent.get(why, 0) + 1
                    continue
                runner = _runner(page)
                if runner is None:
                    if _test_by_line(page):
                        unknown.append((entry, page))
                    else:
                        mentioned += 1
                    continue
                command, why = _command(runner, held)
                if command is None:
                    absent[why] = absent.get(why, 0) + 1
                    continue
                verdict, said = _run(command, page, name)
                if verdict == "red":
                    red.append((entry, said))
                elif verdict == "unrun":
                    skipped.append((entry, said))

    for entry, why in red:
        print(f"RED   {entry}\n      {why}")
    for entry, why in skipped:
        print(f"UNRUN {entry}\n      {why}")
    for kind, entry in mute:
        print(f"quiet {kind:9} {entry}")
    for entry, page in unknown:
        print(f"UNKNOWN {entry}\n      {page}: a test cited by a line runs no test - "
              "cite it by its name after ::")
    for why, count in sorted(absent.items()):
        print(f"UNRUN {count} cited {'test' if count == 1 else 'tests'}: {why}")
    print(f"\n{len(red)} lost their evidence, "
          f"{len(skipped) + sum(absent.values())} were not run, "
          f"{len(unknown)} named nothing a command runs, "
          f"{mentioned} mentioned beside a test, "
          f"{len(mute)} rest on something that never re-runs"
          + (f", {away} in a tree that is not here" if away else ""))
    # A toolchain that was missing leaves the record unchecked rather than
    # clean, and the exit code is the only part of this a script reads.
    return 1 if red or absent or unknown else 0


def main(argv: list[str]) -> int:
    # Answered from anywhere on the line, because the command whose options a
    # reader wants is the one they have already typed. Every command below
    # would otherwise take it as an argument rather than as a question, and
    # `note` would take it as a sentence and write it down.
    if any(word in ("-h", "--help") for word in argv[1:]):
        print(__doc__.strip())
        return 0

    root = _record()
    configure(root, _project(root))
    command = argv[1] if len(argv) > 1 else "state"
    if command == "note":
        note(argv[2:])
    elif command == "find":
        find(argv[2:])
    elif command == "set":
        set_field(argv[2:])
    elif command == "close":
        close(argv[2:])
    elif command == "check":
        entries, broken = load()
        faults = check(entries, broken)
        for fault in faults:
            print(fault)
        ready = worked_through(entries)
        if ready:
            print("\nfinished and not moved - `kb close` it, or say in it what is "
                  "holding it:")
            for entry in ready:
                print(f"  {entry}   [{entry.place}]")
        overgrown = grown(entries)
        if overgrown:
            print("\ngrown by dated notes past its body - rewrite the body to what is "
                  "true now, and move the notes to kb/archive/ under working:")
            for count, entry in overgrown:
                print(f"  {count:>2} notes  {entry.scanned(12)}   [{entry.place}]")
        unshaped = worked_unshaped(entries)
        if unshaped:
            print("\nworked on while still caught - write its criterion and move it to "
                  "scoped/, or split off the thought it started as:")
            for count, entry in unshaped:
                print(f"  {count:>2} notes  {entry.scanned(12)}   [noted]")
        moved = moved_under(entries)
        if moved:
            print("\nclosed, and the code has moved under it - repoint it where the "
                  "sentence survives the move, and write the name as prose where it does not:")
            for line in moved:
                print(f"  {line}")
        if not faults and not ready and not moved and not overgrown and not unshaped:
            # Silence is how a run that never happened looks, so say it walked.
            print(f"{len(entries)} entries, walkable: every link, citation and "
                  f"field a place asks for")
        return 1 if faults else 0
    elif command == "rules":
        return rules(load()[0])
    elif command == "stale":
        if "--dry-run" in argv:
            return dry(load()[0])
        return stale(load()[0])
    elif command == "state":
        entries, broken = load()
        state(entries, check(entries, broken))
    else:
        sys.exit(__doc__)
    return 0


if __name__ == "__main__":
    # A page of output piped through `head` is the normal way to read this
    # tool, and a filter dies quietly when its reader goes away rather than
    # printing a traceback over the lines that got through.
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    raise SystemExit(main(sys.argv))
