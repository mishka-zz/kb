# The entry format

One entry is one file, everywhere. In the queue it is `<place>/<id>-<slug>.md`;
in the reference it is `known/<subject>/<id>-<slug>.md`. Same format, same
parser, so an entry that stops being work and becomes knowledge is a `mv` and an
edit - not a conversion.

Fields are flat `key: value` lines between `---` fences; below them the prose is
unconstrained. No nesting, no lists - several values are separated by commas.
That keeps the parser small, keeps a one-field change to a one-line diff, and
keeps the schema holdable in the head.

**A long field may be carried on indented lines**, joined with a single space:

```markdown
outcome: test: src/tests/test_header.py::TestField::test_a_folded_value_arrives_whole, which
    holds the unfolding rule where a passing run would otherwise cover less and
    say nothing
```

Flat, still - the continuation is a wrap and not a structure, and nothing about
the field's value changes. It is here because `outcome` and `because` are
paragraphs by the time an entry closes, and a paragraph on one physical line is
one nobody reads: not in the file, and not in the diff that changes it. The
indent is tested before the colon, so a continuation may carry a citation, a
line number or a time without reading as a new field.

```markdown
---
id: 10
title: A key split across a continuation line is matched by nobody
kind: work
noted: 2026-08-28
tags: io, release, quiet
criterion: A record whose key arrives split across two continuation lines
    yields the fields the unsplit form yields
related: 12, 16, 19
---

Prose. Subheadings inside it are fine - a thing that has to be read in order is
one entry, not several.
```

## Identity

Counted up in Crockford's alphabet - `0-9` and the letters without `I`, `L`,
`O` and `U`, so nothing reads as a one or a zero and an identity can be said
aloud. A new one is two characters - `1A`, `9K`, `F2` - and carries both a
digit and a letter, in any order, because all digits reads as a plain number
and all letters reads as initials beside the abbreviations this record is
full of; the count skips whatever offers only one kind. The ones already
handed out keep what they were given. A third character when two run out,
and a fourth after that.

A character outside the alphabet - `O` for `0` is the typo a human makes - is
refused on sight. Left in, it takes the tool's one irreplaceable job with it,
because the next identity is counted from the ones already there.

Counting rather than drawing at random buys one thing worth having: a listing
sorts into **the order things were learned**. What it costs is that two sessions
allocating at the same instant would land on the same number.

What guards against that is a look at the directory followed by an exclusive
create, and the exclusive create alone is not enough - a filename carries a slug
as well as an identity, so two different sentences claiming one number produce
two different filenames and both succeed. The window is between the look and the
create, and it is narrow rather than closed. `check` refuses a repeated identity,
and until somebody cites it the repair is a rename.

The identity carries no letter for kind, repository or store. An entry outgrows
all three, and none tells a reader anything.

**Sub-numbers, and why they matter more than they look.** An entry may be split
into `12.1`, `12.2`, and parts may be merged back into `12` at any time. A
citation survives both, because a reference resolves by prefix: a reference to
`12` finds `12.1` and `12.2` when `12` itself is gone, and a reference to `12.1`
finds `12` when the parts were merged.

So **restructuring never breaks a citation**, and cutting an entry down or
splitting one that grew costs nothing beyond the writing.

Each step of the resolution is exact. Going up looks for that parent itself and
never for whatever else is left of its family - so a citation of `35.7` does not
quietly land on `35.1` because they share an ancestor. A reader sent somewhere
plausible and wrong is worse served than one sent nowhere, because only the
second knows it.

## The fields

**The set of names is closed** - what follows is all of them, and a name outside
it is refused. It is what stops a carried line that has lost its indent from
reading as a field nobody wrote, which is silent against an open set and lands
on the fields that carry citations. It catches a misspelled name from the other
side: `critereon` is otherwise an entry with no criterion and nothing to say so.

| | | |
|---|---|---|
| `id` | always | Above. |
| `title` | always | One line. What is true, or what is wrong - not a topic. |
| `noted` | always | Stamped by `note`. |
| `kind` | outside `noted/` | `work`, `fact` or `decision`. |
| `tags` | optional | Free, comma-separated. `state` marks `release`, `quiet` and `needs-human`; `carried` marks a guideline whose occasion was not this codebase's; `check` holds anything tagged `measurement` to the rule below. The rest are for finding. |
| `criterion` | `work`, once shaped | What would show it done. Refused if absent - work without one cannot be finished, only abandoned. |
| `provenance` | `fact` | Where it is re-derived. |
| `because` | `decision`, and anything in `moot/` or `refused/` | The reasoning that would have to fail. Not the conclusion; the title carries that. |
| `outcome` | `done/` | What the work reached, **and the evidence** - written in the same forms as a provenance. |
| `closed` | terminal places | Absolute date. |
| `decided` | optional, on a `decision` | Absolute date. A decision settled somewhere other than a terminal place has no `closed`, and when it was taken is the thing a reader wants next after what it says. |
| `related` | optional | Comma-separated ids. Untyped and undirected: an edge is worth typing only when something acts on the type, and nothing does. |
| `working` | optional | A file **in `kb/archive/`** holding the investigation an entry was cut down from. Checked to be there. |
| `legacy` | optional | Where the entry came from, when that is somewhere with a name of its own: `legacy: TODO.md "Start here"`, `legacy: D-15`. A retired planning document carries its items under headings or old numbers, so an entry migrated out of it says which, and `kb find d-15` lands. Not an index - what it names is frozen, so nothing can fall out of step. |

## Provenance, and what closing has to do with it

A provenance opens with one word saying what kind it is, because the kind
decides its upkeep. The first two fail by themselves; the rest fail silently or
not at all, and marking them apart is the only way that difference stays visible.

A field resting on more than one kind carries each in turn, a semicolon and the
kind's word opening the next: `test: src/tests/test_x.py::test_y; measured:
kb/archive/the-runs/`. A part starts wherever a kind's word and its colon start
a word - after a semicolon, a full stop, `and`, or a bracket alike - and never
inside a path. Each part keeps its own kind's upkeep, and `stale` runs only the
tests written under `test:`.

| | | goes stale by |
|---|---|---|
| `test:` | a test that fails if it stops being true | **failing, loudly, by itself** |
| `gate:` | a `GATE` line an acceptance run prints | **failing, loudly, by itself** |
| `source:` | somebody else's source, at a file and line | the upstream moving. Silently |
| `cited:` | a standard, a paper or a book - the document and the section, by name | a new edition, an erratum, or a bad transcription. Silently |
| `measured:` | measured in a session, **naming what it was measured against** | the world moving. Silently |
| `judged:` | experience. Nothing re-derives it | never, because it never claimed to |

`judged:` is allowed deliberately. A record that refuses experience does not
stop having it; it gets experience smuggled in dressed as measurement. Named, it
stays visible - `state` lists every fact resting on anything that does not
re-run, by name.

**A `test:` must be a test that fails when the fact stops being true**, which is
a stronger thing than a test that mentions the same subject. `check` accepts a
citation to a test that exercises a neighbouring case, because a checker can see
that the name exists and never what it measures. That is the format's easiest
mistake and its least visible one.

A path may carry a line - `page.go:82`, `parse.go:126-207` - and the line is
part of the citation and not part of the path. **The line itself is never
checked**: nothing can confirm a number that addresses no name. So a `source:`
citation is held to the file existing and to whatever name is written after the
`::`, and never to position - which is exactly the way it goes stale, and why
it is marked as going stale silently.

**Prefer a name to a line, and say which release a line is true of.** A tree
`project.md` names as `outside` is released on its own cadence: a line number
that addressed a function in one build addresses something else two tags later.
A name survives what a line does not.

**Every citation is written from the project root**, and a name is reached
through it. `src/tests/test_header.py::TestField::test_unfold` is read by
`check` and runnable by `stale`. None of these is read by either, and each is
refused for that reason - the strongest-looking form, reaching nothing:

```
test_header.py::TestField::test_unfold
tree/walk.go::Walk
::test_unfold
```

The first is a basename, the second a package-relative path, the third carries
on from the sentence before. A title and a body are held to it as a field is: a
basename resolves only while one file happens to carry it, and a tree easily
holds one `README.md` per directory. What is inside a fenced block is not held:
that is a command or a quotation, and rooting it would break it.

Nor is a citation broken across a line after the `::`, which is what wrapping a
long one carried on an indented line produces: the path matches, the file is
there, and the name goes unread.

**A name is held to being *defined* in the file, not mentioned in it.** The day
a function leaves a file, the file names its new home in a comment, and a word
match survives the one event the citation exists to catch. Python is parsed:
`Class::method` and `Class.method` are asked as one written inside the other, a
name quoted in a fixture string is not a definition, and one bound beside
another in a tuple is. A file the running interpreter cannot parse - written
for a newer Python - is held to the word instead. Go is read by declaration: a
function, a method on any receiver, a type, a var or a const, alone or grouped;
`Type.Method` is a method on that type or a member of it; what follows a test
function is a subtest, which Go declares nowhere, and is held to the word.
Anything else is held to the word: a test of any other kind cited as
`path::name` passes `check` only where `name` appears in that file as a word.

**A closed entry is reported rather than refused** where the code has moved
under its title or its prose. Those carry a date and say what was true on it,
and `SKILL.md` beside `kb.py` says what to do with the listing. Its other fields fail like
anybody's.

**Which command runs a cited test is decided by the file's name, and the
record's `runners` field says how.** Each pattern there is matched against the
name of the file a citation names, in the order written, and the first that
matches hands the path and the name, as the citation writes them, to its
command under the record's `run/`. Any other path written under `test:` is a
**mention** - the code a test covers or the helper it drives, named in a
sentence about the test - and no command is asked to run it; `--dry-run` lists
it and `stale` counts it. A test file cited by a line is **unknown**: it
addresses no test, `stale` lists it and fails, and the repair is to cite the
test by name. A record whose `runners` is empty runs nothing, and `stale` says
so once, counts every cited test as not run and fails.

**For a Python test, prefer the full address, class and all** -
`src/tests/test_header.py::TestField::test_unfold`. A bare name is
accepted, and the command running it then has to find the class - and should
**refuse to guess** where the name lives in more than one, rather than validate
a fact by running a different test. Writing the class removes that risk and is
the form a test runner takes unaltered. `check` accepts either, and holds the test to being
written in that class - both halves existing somewhere in the file is the shape
a rename leaves behind, and the one pytest refuses to collect.

**For a Go test there is nothing to guess** - a test name is unique within its
package, so `src/header_test.go::TestAFoldedValueArrivesWhole` is the whole
address. A further `::` is a subtest and becomes an anchored `-run` path.

A citation may name a **directory** - a corpus, a source tree - and then no
name follows the path, there being nothing in a directory to find.

**`outcome:` takes the same forms**, which is the point of it. Closing a task is
then exactly as evidenced as recording a fact, and one mechanism serves both.
One line, like any field:

```
outcome: test: src/header_test.go::TestAFoldedValueArrivesWhole
```

`kb stale` runs every `test:` in the record and prints what went red, beside
everything resting on a kind that was never going to move. A test that skipped
prints `UNRUN`, because a skip exits zero and is the absence of evidence; the
command says so by exiting 77. A Go `-run` that matched no test prints `RED`,
because it also exits zero and says `ok`, which is the same absence wearing the
shape of presence.

## References

A `[[id]]` anywhere in any prose, inside `kb/` or outside it. `check` resolves
every one it finds across `kb/` and the documents `project.md` names as
`citers`, by prefix, and reports the ones leading nowhere.

It resolves nothing inside a tree that ships without the record, and none
should be written there: a reference from such a tree into `kb/` is one its own
readers cannot follow.

## What a record says about itself

`kb/project.md` is the one file the tool reads that belongs to the project
rather than to the format. It carries the same flat `key: value` head an entry
does, between the same fences, and any prose after them is the project's own.
Every field is optional and comma-separated; the record's own directory is
always owned and always a citer, whatever the file says.

| | |
|---|---|
| `owned` | The trees a citation may name and be checked against - `src, vendor, docs`. A path starts with one of them; the same name inside another path - a URL, somebody else's tree - is a reference, not a citation. |
| `outside` | Of those, the trees a working copy may be without: released on their own cadence, cloned on their own. A citation into one that is entirely absent is passed over, by `check` and by `stale` alike; a missing file inside one that is here fails. |
| `citers` | Documents outside `kb/` in which a `[[id]]` is resolved - `AGENTS.md, TODO.md`. Only what travels with the record. |
| `documents` | Documents read for what is true *now*, and so held to a citation the way an entry is - the agent instruction, a deferred-work list. Never a record of a day. |
| `source` | Trees and files `note` and `find` search beside the record, so what already stands answered next to the code is found on the way past. |
| `skip` | Directory names that search passes over inside those trees - a vendored copy of somebody else's code, which answers nothing about the project's own and outnumbers it. |
| `theirs` | Subjects under `known/` holding what somebody else's software does, offered one link further out under `find --near`. |
| `figure` | A regular expression for a measured quantity in prose, in the project's own units. `stale --dry-run` lists entries carrying one that nothing re-derives. |
| `runners` | Which cited files are tests, and the command under `run/` that runs each - a filename pattern and a command name per pair, tried in order: `test_*.py run-pytest, *_test.go run-go-test`, each command one the project writes. Empty, `stale` runs nothing and says so. |

```markdown
---
owned: src, vendor, docs
outside: vendor
citers: AGENTS.md, TODO.md
documents: AGENTS.md, TODO.md
source: src, AGENTS.md
skip: vendor
theirs: kernel
figure: \b\d+(?:\.\d+)?\s*(?:%|ms|MB)\b
runners: test_*.py run-pytest, *_test.go run-go-test
---
```

## What refuses an entry

`check` fails on these and nothing else. Every one asks whether something is
**there**:

1. A file that does not parse, or carries no id or no title. A file that cannot
   be read is a fault and never a silence - dropped quietly it would leave the
   numbering, and the next `note` would hand out a number in use.
2. A repeated id.
3. Outside `noted/`: no `kind`, or one that is not the three.
4. A shaped `work` with no `criterion`.
5. A `fact` with no `provenance`, one not opening with a known word, or one
   naming a file or a test name no longer there.
6. A citation anywhere in an entry - a field, the title, the prose, `noted/`
   included - naming something inside a file with no path to reach it by, or
   with the name carried to the next line. `::` is also how C++ spells a scope
   and how a Go doc comment reaches a method, and `std::vector` is not a
   citation: what separates one is that it names a file.
7. A title or prose naming something inside a file -
   `src/header.py::Field.unfold` - that the file does not define. The
   **name** only: a bare path in a body is English, and so is a path that has
   gone, the record's subject including what was deleted. Reported rather than
   refused where the entry is closed. A tree named as `outside` that is not
   checked out at all is passed over wherever it is cited, since a citation
   into it says nothing about the record.
8. A citation naming a name inside a name - a class and a test in it, a type
   and a method on it - where each is not written inside the one before it.
   Python is parsed for this, Go is read by declaration, so a definition quoted
   inside a string is not one and a pair of names bound together is two.
9. A field written twice. The second replaces the first, and what it replaced
   reaches neither this nor `stale`.
10. Any of 6, 7 and 8 in a document `project.md` names as `documents`. Those
    are read for what is true now. `kb/archive/` is a record of a day and is
    not walked.
11. A `decision` with no `because`; anything terminal with no `closed`; `done/`
    with no `outcome`; `moot/` or `refused/` with no `because`.
12. A `working:` naming a file that is not there.
13. A `[[id]]` or a `related:` that resolves nowhere, even by prefix. A
    bracketed word that is not an identity at all is left alone.
14. An entry tagged `measurement` that names nothing in `known/status/`. That is
    the rule bounding this queue: measuring can always be done more finely, and
    the only thing that says when to stop is a number somebody claims.
15. A file that sits directly in `known/` rather than under a subject; a head
    line that is neither a field nor prose; an id its own filename does not
    carry.

## What it points out without refusing

Closing is written **before** the file is moved - `kb set` and then `kb close`,
which refuses to move an entry the place would not hold - and the demand then
lands while the answer is still in somebody's head. The cost of
that order is a window: an entry can carry everything a terminal place asks for
and still be in the queue, and the directory - which is the state - does not
know.

So `check` ends by listing any entry outside a terminal place that carries an
`outcome` or a `closed`. It is a **prompt and exits zero**: there are good
reasons to hold one open, a second reader who has not been through it or a test
tier not yet run, and the entry's own prose is where those belong. What there is
no good reason for is nobody noticing.

It lists, the same way, a shaped entry carrying more dated notes than a closure
ordinarily takes - the adversarial tester's finding and the review. Past that
the notes have overtaken the body, and the body wants rewriting to what is true
now with the notes moved to `kb/archive/` under `working:`. `noted/` is left
out, being a scratchpad until somebody shapes it.

It ends the same way for a **closed entry the code has moved under**: one whose
title or prose names something its file no longer defines. A closed entry is
dated and says what was true on that date, so failing it would be pressure to
repoint the path, which is backdating - and where the entry's own work replaced
what it diagnosed, a repointed path is a false statement about today's code in
the record's strongest form. So it is listed, and the reader decides one at a
time: repoint where the sentence survives the move, and write the name as
ordinary prose where it does not. The entry's `outcome` is held whatever the
place, being what a reader is sent to.

Nothing runs `check` automatically unless the project arranges it - a record's
directory is often outside version control, so there is no commit to hang a
hook on. Run it at the moment a hook would have: when you have just finished
something.

**None reads what a field says**, and none ever will. `criterion: fix it` and
`because: it is better` both pass. Whether two entries say the same thing, or
whether a criterion is any good, is a reader's judgement - the tool's whole job
is to make sure the reader can find what they need.
