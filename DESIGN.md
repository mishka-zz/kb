# Why kb works the way it does

`README.md` says what kb is for and when to use it, `INSTALL.md` how a project
takes it on, `SKILL.md` how an agent works the record and `schema.md` what a
file in it may say. This page is the reasoning behind all of them: why each
part behaves as it does, and what failed before it did.

Everything a project has learned and everything it has open, one entry to a
file, in a `kb/` directory at the project's root. The tool that keeps it -
`kb.py` and these pages - belongs to no project and serves every record on the
machine; `kb/project.md` is where a record says what it is about, and it is the
only file the tool reads that is the project's rather than the format's.

The project's own agent instruction - `AGENTS.md`, or whatever its agent
reads - says where things are and which document decides. The record says what
is known and what is left, and the two do not overlap: an index that also held
knowledge would be a second copy of it.

---

## Where the project stands

```
kb                        where the project stands
kb note "a sentence"      catch it; an identity comes back
kb note 12 "more"         add to what is already caught
kb --help                 every command and every option
```

`kb` is whichever command reaches `kb.py` - `tools/kb/kb.py` through a link in
the project, or `kb` on the path - and it finds the record from wherever you
stand inside the project, the way a version-control command does; `$KB_RECORD`
names one where that does not apply.

The rest of this page is why those behave as they do; `--help` is what they are,
and it answers from any command line rather than only a bare one. A copy of the
list here would be a second thing to keep true, and only one of the two is
checked by being run.

`find` searches every field and the prose. A hit's score is **the share of the
question it answers**, weighted by how rare each word is - a word every entry
carries counts for little, a word nothing carries counts for most, so a question
half of which the record has never heard of cannot score above a half. It is not
term frequency times inverse document frequency: a repeated word says nothing
when an entry is one claim, so only the rarity survives, and what that buys is a
number bounded by one that means the same thing across two different questions.

Nothing is hidden. The header says what the **best** hit answered, and says so
when that is thin - a record consulted and silent then reads differently from
one searched badly, without an entry being dropped for sharing few words with
the question. `--floor 0.5` cuts for a caller that would rather have the cut.

A title too long for a line is **folded** where the output is scanned - the
queue, a page of hits, the cards under `--near` - and printed whole where it is
read: the entry `--near` opens, `--full` and `--fields title`. Catching something costs no decisions, so a
draft's title is routinely a paragraph, and a paragraph in a listing hides the
entries beneath it.

`--field kind=fact`, `--field provenance=judged`, `--field place=analyzed` narrow
it, and they stack - `--field place=analyzed --field tags=io` is what is open
on one subject, which is the question a sprint is picked from;
`--fields title,provenance` reads a column; `--full` reads whole entries;
`--limit` and `--page` turn the pages; `--near 12` returns an entry whole and a
card for everything one link away - where each stands, which way the link runs,
and the field that decides whether to open it - and under them what *somebody
else's software* does a link further out - the measurements of what we do not control that reach the task
through a neighbour, which is where a fact nobody thought to link from here goes
unread. A long entry is held back a little in the ranking, because breadth is
not an answer: one whose prose spans the record answers a part of every
question and would arrive beside the entries that are about it. Numbers and
mixed words - `100`, `mb`, `x86` - are terms like any other.

Runs from anywhere. **Nothing is stored that could be searched for instead** -
no summary, no table of contents, no per-subject preface. A stored answer goes
stale the moment the record moves under it; a search cannot, because it computes
rather than keeps.

An index would only carry relations between entries, and three mechanisms
already carry those: a `related:` field, subheadings inside one entry, and
merging two entries when they turn out to be one. Where two entries jointly
decide something, that something is itself a claim - so it is an entry, with
`related:` naming both, and `check` can resolve it. A paragraph in an index
cannot be resolved by anything.

What the project *is* - its layout, what each document decides, the rules
across its parts - is the project's own instruction and specifications, and
those stay outside. Everything here is what we have learned, or what is left to
do.

---

## Where the boundary runs

`kb/project.md` draws it. `check` resolves a `[[id]]` written in `kb/` and in
the documents the record names as `citers`, and **nowhere else** - a citation
written inside a tree that ships without the record is one its own readers
cannot resolve. What a component has to say about itself belongs in its own
specification.

The traffic runs the other way instead: `note` searches the trees named as
`source` as well as the record, so what already stands answered beside the code
is found on the way past.

A citation *into* a tree named as `owned` is ordinary and is checked -
`src/header.py`, `src/tests/test_header.py::TestField::test_unfold`,
`vendor/spec.txt`. A name after the `::` is held to being *defined* in the file,
not mentioned in it, and a name with no path to reach it by is refused wherever
it stands - in a title and a body as much as in a field. A tree named as
`outside` that is not checked out at all is passed over rather than failed:
such trees are released on their own cadence and cloned on their own, so a
reader without one is not holding a stale record. A file missing from a tree
that *is* here is a citation gone bad, and fails.

---

## What this is for

**The knowledge is the point.** A queue of tasks is a solved problem with tools
for it; what no tool provides is a record of what a project has learned that
**reading its code cannot tell you**:

| | why the code is silent |
|---|---|
| what somebody else's software actually does | it is somebody else's source, and most of it is behaviour rather than text - and where that behaviour and the document describing it part, agreeing with the behaviour is the requirement |
| how accurate an answer is, and how that is known | a bound is not written in the thing it bounds |
| what we tried and put down | **it is nowhere at all** - not in the code, not in the tests, not in the history if it never reached a commit |
| how to work here | nothing about method survives in source |

The third row is the one that cannot be recovered at any price. Everything else
can be re-obtained by paying again: measure the model, read the code, derive the
invariant. A road not taken leaves no trace, and six months later somebody
proposes it again in perfect confidence.

So the record has an internal priority: **what is irrecoverable, then what is
expensive, then what is merely convenient.**

It follows that this is not a replacement for comments. Where a fact governs one
function, the comment beside it is the better home, because a reader changing
that file cannot miss it. An entry here that restates a comment is a second copy
that can disagree with the first.

---

## The one rule the rest follows from

> **An entry states something, and names the thing that could prove it wrong.**

Work names what would show it done. A fact names where it is re-derived. A
decision names the reasoning that would have to fail. An entry naming none of
those is not refused - it stays in `noted/`, where nothing is promised.

The rule was not chosen in advance. It is what three failures had in common: a
figure in prose nothing re-ran, wrong for weeks while tests stayed green;
cross-references to items closed and removed, still pointing readers at a file
that no longer held them; and a closure convention that seven finished entries
did not follow, because nothing asked them to.

---

## Two stores, because they answer opposite questions

**Work is a queue.** Order matters, the set changes daily, the question is
always "what is open". Files that move suit that, so the directory is the state:

```
noted/      caught. A sentence, and nothing else is required
analyzed/   shaped: it has a kind and a criterion. Shaped is not verified
scoped/     taken into the scope of work: what is done before the rest
done/       finished      moot/  it stopped applying      refused/  not to be done
```

Changing state is a move - `mv` between the open places, `kb close` into a
terminal one - and no field holds a copy of it, so the two cannot
disagree and there is nothing to file afterwards. That is the design's
load-bearing decision, and it comes from what actually rotted: closure used to
be several separate acts at the moment of lowest attention, and twenty-odd
entries sat closed among the open ones while references pointed at nothing.

**`scoped/` is the scope of work, not the task in hand.** Which entry is being
worked this hour is plain from the session, and it rarely outlives a session or
two. What gets lost is which of the ready entries were chosen to be done next,
because that was said in a conversation and a compaction takes it along with
everything else that was never written to a file. So an entry moves into
`scoped/` when it is taken into the current body of work, is worked where it
stands, and leaves from there for `done/`, `moot/` or `refused/`. One that drops
out of the scope unfinished goes back to `analyzed/`. `kb` prints the scope
first, so keep it to what is actually intended next.

**Knowledge is a reference.** Order does not matter, the set is stable, the
question is always "what do we know about X". So it is gathered by subject:

```
known/<layer>/    what one layer of the code does, and what it decided where
                  its documents are silent - one subject per layer
      <theirs>/   what somebody else's software does - an engine, a client,
                  a kernel; the behaviour no document decides and the corpus
                  had to settle. Named in project.md as `theirs`
      ours/       what our own code does across layers, and what our
                  measured limits cost
      status/     what the project claims, one entry per bar
      decisions/  what was settled, and why the alternative was put down
      guidelines/ how to work here: method, review, testing craft
      literature/ what the published work establishes, and where it stops
```

**A subject exists once something is in it. There is no empty one waiting**, and
the list above is a shape rather than an inventory. Create one by putting an
entry in it.

`known/status/` holds what the project **claims**: one entry per bar - an
error share, a memory ceiling, a throughput on the hardware it has to run on -
each carrying a `gate:` provenance and the reasoning for where the bar sits,
and beside those the framing they share: how a bar is computed at all, what a
measurement has to hold still to be about the thing it names, and what is
claimed with nothing running behind it. Only the claims themselves have a gate;
the framing is decision and method, and reads as such.

It also bounds the queue: an entry tagged `measurement` must name a claim in
`known/status/` that it defends, or `check` refuses it. Measuring can always be
done more finely, and a stated number is the only thing that says when to stop.

One file per entry there too, so a subject grows without anything having to be
restructured, and an entry moving from the queue into a subject is a `mv`.

---

## Rules that were carried rather than earned

Every entry in `known/guidelines/` tagged **`carried`** states a rule this
project has not yet met the occasion for. The rule and its mechanism are
whole; what is missing is a case from this codebase, and each says so - its
provenance names the evidence it came with, which is somebody else's.

`--field tags=carried` lists them. When one of them is met here - and it will
be, in this codebase's own terms - rewrite the entry on that occasion and drop
the tag. A rule with a case behind it is worth more than the same sentence
without one, and the tag is what says which is which.

The tag is not a licence to import. A rule arrives because its mechanism is
whole and the failure it names can happen here; one that needs the other
codebase to be a particular way is not carried, it is guessed. What stays
behind is the other record's occasions, its specimens and its numbers - the
mechanism travels and the case does not, which is what the tag records.

---

## The motion a project makes most often

A claim nobody has measured is **not** a fact. It is work, and the work is to
obtain the provenance.

```
something does not add up  ->  note "…"       a sentence, an identity, and what
                                              is already near it - entries and
                                              source both, printed unasked
it accumulates             ->  note 10 "…"    dated, appended
it is shaped               ->  analyzed/      kind, criterion - by hand
it is taken into the scope ->  scoped/        worked there, and closed from there
the measurement lands      ->  known/<subject>/   kind: fact, provenance: test: …
the rule settles           ->  the entry is cut down to the rule; the working
                               moves to archive/ and `working:` points at it
```

The identity never changes, and a citation survives a later split or merge
because references resolve by prefix - each step exact, so nothing lands on an
unrelated sibling. Restructuring therefore costs nothing beyond the writing.

---

## Who does what

| | |
|---|---|
| **the tool** | hands out an identity and appends; retrieves; keeps the record walkable; writes a field and moves an entry to a terminal place when told to, refusing what `check` would refuse |
| **the agent** | everything needing judgement: shaping, deciding what a field says and that work is finished, cutting down, correcting, retiring - and deciding whether two entries are the same thing |
| **the harness** | puts the record in front of the agent - two commands at the top of the project's agent instruction - and asks nothing else of it |

The first two are what a directory and a text editor cannot do. In particular
`check` is **not** a guard on quality: it asks whether a field is there, never
what it says. `criterion: fix it` passes, and no checker will ever catch that.
Content is the reader's business; the tool's job is to make sure the reader can
find what they need. That separation is the design, not a shortfall of it.

What it *can* answer is a **name**: an entry writing
`src/header.py::Field.unfold` is making a claim that file defines or does not,
in a title and a body as much as in a `provenance:`. So write the
name where you are resting on one. It is the only part of a reading a tool can
keep honest, and the readings nothing re-runs are the ones that go quietly
wrong.

---

## The record is a map, and it is consulted rather than filed into

Knowing where you are going, go; not knowing, look. Nothing here asks for an
entry to be written before code can be, and nothing treats a `mv` between queue
directories as a precondition for work - that would turn the record into
bookkeeping, which is the one thing that reliably stops being done.

**Reading is asked for rather than fired**, and that is a measurement rather
than a preference, made on the first project this record was kept for. Output
printed at the top of a session sits at the far end of everything that arrives
after it; the rules do not leave the context, they lose to two hundred thousand
tokens of newer and more specific material. Printing them again does not beat
that, because it competes on the axis it is losing on. So the two commands are
an instruction in the project's agent instruction, which is read as work to do.

Three other moments were tried and dropped: speaking when the code was edited
with no entry in hand, asking for a summary before a compaction, and printing
the rules after one. The first two turned a reading tool into a form, and the
cost of that lands on every change while what it prevents is occasional. The
third was answering the wrong question, above.

---

## What reading is owed at each moment

Since the tool cannot judge, the depth of reading is what has to be right - and
it differs by moment, because the *mistake* differs by moment.

| moment | how wide | how deep | the mistake it guards |
|---|---|---|---|
| catching something | everything that matches - printed by `note` itself, from the record **and the source** | skim, then read the two or three closest | inventing again what is already known |
| picking it up | the entry plus one link - `find --near` | read it all, hold it | working without the mechanism, the roads already put down, or the facts it rests on |
| recording a measurement | search the subject, then `--near` the closest hit | read those | answering a question the record already answered, or answering it a second way |
| closing it | this one entry | read it against the code, then **run the tests** | claiming more than the change reached |

At creation the mistake is re-invention, so wide and shallow wins; at closure it
is overclaiming, so narrow and verified wins. Attention is not a ration spread
evenly - each moment needs it on its own axis.

`note` searches the source trees as well as the record, and that is not a
courtesy. The failure it answers: a constant was chosen while the same question
stood answered in another module, one `grep` away. A record that searched only
itself would have missed it too.

---

## Layout

```
the tool, once per machine
├── kb.py       - note, find, set, close, state, rules, check, stale. Standard library, no git
├── test_kb.py  - every rule that refuses an entry, and proof that it fires
├── test_run.py - the sample command held to the contract it samples
├── README.md   - what it is for, for a person
├── INSTALL.md  - taking it on in a project, for the agent doing it
├── SKILL.md    - working the record, for an agent
├── schema.md   - the format          DESIGN.md - this page
├── LICENSE     - BSD 2-clause        LICENSE.0BSD - kb.skel/, free to copy
└── kb.skel/    - a record to copy, as /etc/skel is: project.md to fill in, the queue,
                  the guidelines, and run/ - the contract for running a cited test and a sample

<project>/kb/   the record, once per project
├── project.md  - what this record cites, which documents it holds, what runs its tests
├── noted/ analyzed/ scoped/ done/ moot/ refused/  - the queue
├── known/<subject>/                               - the reference
├── run/                                           - the commands `stale` runs a cited test with
└── archive/                                       - workings cut out of entries
```

The tests are run with pytest, which the tool itself does not need:

    python3 -m pytest test_kb.py test_run.py

---

## Nothing runs `check` for you

Unless the project arranges it. A record's directory is often outside version
control, so there is no commit to hang a hook on; run it at the moment the hook would have - when you have just finished
something - and read the lists it ends with: entries carrying an outcome that
have not moved yet, and closed entries the code has moved under.
