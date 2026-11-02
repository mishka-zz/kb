---
name: kb
description: How to catch a thought, record what was measured, settle an argument and close work in a project that keeps a kb/ record - and what to read before each. Load before opening an entry, moving one, or writing down anything established.
---

# Keeping the record

**Run `kb rules` before anything else.** It prints every guideline this
project holds - `known/guidelines/`, one line each, the title carrying the
rule. A rule you have to remember to look up does not fire: nobody searches for
*do not trust that number* before trusting it, or for *a reviewer's finding is a
hypothesis* before acting on one. So the set is read at the start, unasked,
while it still costs nothing.

Each line has an entry behind it with the mechanism and the occasion that taught
it. `kb find --near <id>` opens one, and the moment to do that is when you
are about to trust a figure, a review, a test's name, or your own recollection
of how something behaves.

A rule tagged `carried` has the mechanism but not an occasion from this
codebase. It is a rule, not a suggestion; what is missing is the case, and the
first time one turns up here the entry is rewritten on it and the tag comes off.

| | when |
|---|---|
| `kb rules` | **first thing in a session**, before any work |
| `kb` | straight after, for where the project stands |
| `kb note "…"` | the second something is noticed |
| `kb note 10 "…"` | whenever more is learned about it |
| `kb find …` | before starting, before choosing a number, before proposing anything |
| `kb set 10 outcome "…"` | writing a field you have decided on - one field, every other line left as it was |
| `kb close 10` | once the outcome is written; `kb close 10 moot` or `refused` once the `because` is |
| `kb check` | when you have just finished something - nothing runs it for you |
| `kb stale` | when a refactor has moved tests, or before a release - and read below first |

`kb` is whichever command reaches `kb.py` - `tools/kb/kb.py` through a link in
the project, or `kb` on the path; `INSTALL.md` sets one up. It finds the record
from wherever you stand inside the project - the first `kb/` holding a
`project.md` upward from here - and `$KB_RECORD` names one where that does not
apply. `project.md` is where a record says which trees it cites and which
documents it holds; `schema.md` beside this file lists its fields.

`find` reaches every field and the prose, and scores each hit as the share of
the question it answered - so a low number is information rather than noise, and
the header says outright when the best of them is thin. Nothing is dropped;
`--floor` is there if you want it dropped. Narrow with `--field kind=fact`,
`--field provenance=judged`, `--field place=scoped`, and stack them - what is
open on one subject is `--field place=analyzed --field tags=io`, and it is
the question to ask before picking work rather than reading the queue by eye;
read a column with `--fields title,criterion`; read whole entries with `--full`;
page with `--limit` and `--page`. An option nobody defined stops the search
rather than being swallowed as a search word.

`check` **has no hook behind it** unless the project gives it one. A record's
directory is often outside version control, so there is no commit for a hook to
hang on, and the one check that must not be voluntary is then voluntary. Run it
when you have just closed something: that is the moment it was designed to
arrive at, and it ends by listing any entry that carries an outcome and has not
moved, and any closed entry the code has moved under.

`stale` **runs every cited test for real**, through a command the record keeps
under `run/`. Which files are tests and which command runs each is the
record's `runners` field in `kb/project.md` - `test_*.py run-pytest` - matched
against the file's name, and nothing else goes anywhere. Any other path under
`test:` - the code a test covers, the helper it drives, a results file beside
it - is a mention: run by nothing, failing nothing, and listed by `--dry-run`.
A test file cited by a line is `UNKNOWN` and fails the run, since it names a
test and addresses none: cite it by name. How a test is run - which
interpreter, which toolchain, from which directory - is the project's, so the
record writes its own commands; `kb.skel/run/README.md` is the contract and
`kb.skel/run/run-program` a sample of it. A record naming no runner has its
cited tests counted as not run, said once. Each command is asked once whether
its toolchain is there. A command
the record does not have, or one saying its toolchain is not there, is reported
**once**, with the tests it owned counted as not run - not as anything else, and
`stale` exits non-zero, since a record it could not check is not a record it
found clean.

A command reports a skipped test as not run, and `stale` prints `UNRUN`, because
a skip is the absence of evidence and must not read like the presence of it. A
run that matched no test is worse, since many runners exit zero over it and say
`ok`: a command reports it red.

**Write the name, and write the path that reaches it.**
`src/header.py::Field.unfold` is a claim `check` can answer - that file defines
the name or it does not - where the same sentence written as prose beside a
path is one nobody will notice going wrong. It costs a moment where you are
resting on a function, a type or a test by name, and it is worth it exactly
there: an analysis is the entry nothing re-runs, and so the one most likely to
be quietly overtaken.

**From the project root, always, and in a body as much as in a field.** None of
these is read by `check` - it cannot find the file:

```
header.py::unfold
tree/walk.go::Walk
::unfold
```

The last carries on from the sentence before it, and the first two are a
basename and a package-relative path. A basename resolves only while one file
happens to carry it, and the day a second is added every citation written that
way turns ambiguous at once, in a change that touched none of them. A reader
has the same problem: a tree easily holds a `README.md` or a `specification.md`
per directory. In a field the same form also stops `stale` running the test.

A path on its own in a body is left alone, and so is a file that has gone from
under one, because the record's subject includes what was deleted. So is
anything in a fenced block: a pasted test address is a command that runs from
its repository, and rooting it would break the command to quiet a checker.

**Write it on one line.** A citation wrapped after the `::` reports the file as
there and never reads the name, which is how a long one in a field carried on
indented lines goes silent.

**Defined, not mentioned.** The day a function leaves a file, the file names
its new home in a comment, and a citation held to the word survives the one
event it exists to catch. So a Python name is parsed for - `Class::method` is a
method written inside that class, and a name quoted in a fixture string is not
a definition - and a Go name is held to its declaration: `Type.Method` is a
method on that type or a member of it, and a subtest, which Go declares
nowhere, is held to the word. A bare test name is still accepted, and is a
claim that the file holds it and nothing about where.

The same rules hold in the documents `project.md` names as `documents` - the
agent instruction, a deferred-work list - which are read for what is true now.
`kb/archive/` is not walked: it is a record of a day, like a closed entry, and a
listing that never empties is one nobody reads.

**A closed entry's title and prose are reported rather than refused.** They
carry a date and say what was true on it: a function may be in one file when
one entry closes and in another when the next does, and both entries are right.
Failing the run there is pressure to repoint the path, which is backdating, and
where the entry's own work replaced what it diagnosed it writes a false
statement about today's code in the strongest form the record has. The run says
which closed entries the code has moved under; repoint the path where the
sentence survives the move, and write the name and the file as ordinary prose
where it does not. `git log -S <name>` says which in a few seconds: the commit
that took the name out of the file, and whether the same commit wrote it into
another. Ask it before a pass over the listing rather than after one. Its other
fields are held whatever the place: an `outcome` is evidence a reader is sent
to, and `stale` runs it.

**A citation into a tree released on its own cadence is a citation into a
release.** Where `project.md` names such trees as `outside`, a line number in
one is true of one release and quietly false of the next. Prefer a name over a
line, and where a claim is about a specific release, say which.

Everything else is judgement: shaping a draft, deciding it is finished, cutting
it down, retiring it, deciding two entries are one. The tool does the mechanics
of two of them and none of the deciding. `set` writes one field and reads the
file back before keeping it, because a replace by hand in the head can lose its
closing fence and nothing notices until the next `check`. `close` dates an
entry and moves it, and only once the place it is going to would hold it.

## Catching something

You are deep in something and it does not add up. Say so and keep going:

```
kb note "the retry reads the deadline backwards; I am in the scheduler and
         cannot stop for it; see also how the queue is drained on shutdown"
```

One command, one string, two seconds. **Nothing else is required** - not a kind,
not a criterion, not a tag. An entry that costs a decision to write is an entry
that does not get written, and the thing noticed at minute forty is the most
worth keeping and the first to be lost when the context is compacted.

The one thing it is held to is the form above: a sentence naming a function by
its basename is refused at the next `check`, and the message says what to
write. That is a rewrite of one reference and not a decision, which is why it
is the only thing asked here.

It prints an identity and, under it, **what is already near what you wrote** -
from the record and from the source trees both. Read that before going further.
It is not a courtesy: a constant was once chosen while the same figure stood in
another module for the same reason, with its reasoning written out. The failure
was not that search was bad; it was that nobody thought to search. So the search
happens on the way past, unasked.

Then keep adding as you learn:

```
kb note 10 "not the deadline - the clock is read before the retry count is
            reset"
```

Each line is dated. The entry is a scratchpad and is allowed to be a mess.

## Shaping it

Later - not in the same breath - read the scratchpad, throw out the dead ends,
keep the mechanism, decide what it is, and `mv` it to `analyzed/`.

**An entry being worked is shaped first.** Once a caught thought is being
measured, argued or built against, it is work, and work in `noted/` has no
criterion to finish it by and is invisible to whoever reads what is in scope.
`check` lists a caught entry whose dated notes run past what catching a thought
takes, and `kb` says how many there are.

**Rewrite it where it lies, and move it afterwards.** Shaping usually means
replacing the text outright, and the natural motion for replacing text is to
write a new file - at which point the same identity is in two places, which is
the one thing this layout cannot survive. Editing in place keeps the two acts
apart: the writing changes what the entry says, the `mv` changes where it
stands, and neither can be mistaken for the other. The same holds for an entry
graduating into `known/<subject>/`.

**Write the criterion before the prose.** It decides whether the entry is
admissible at all, and writing it last means writing it to fit whatever the
prose ended up saying.

A criterion states an observable, not an activity. *"A record whose key
arrives split across two lines yields the fields the unsplit form yields"* is
one. *"Fix the key matching"* is not: it can only be declared finished, never
shown.

**Name the population, and the measurement that decides the design.** A
criterion saying only what will be true at the end hands the next reader an end
state and no first move, and the first move is nearly always a measurement:
what does this layer do over its whole set *today*, before a line is written?
Where a criterion names the set - a class of specimen in the corpus, the
inputs a sweep runs over - that measurement is handed over with the work, and
it is the cheapest moment to find out that the design is wrong, or that the
fault is somewhere else. Where it names none, the measurement gets postponed
until after the code, which is where a wrong design costs a day instead of an
hour.

If the entry has grown into two things, split it into `10.1` and `10.2`. If two
turn out to be one, merge them back. Citations survive both, so neither costs
anything - and an entry that is never restructured is how a subject turns into a
wall of prose.

## Writing down something you measured

Ask one question first: **what would re-derive this?**

- **A test** - write the test, then the entry, `provenance: test: …`. The test
  is the fact; the entry is its index. Cite a test that **fails when the fact
  stops being true**, not one that merely touches the same subject: `check` can
  see that a name exists and never what it measures, so a wrong citation here is
  invisible and the strongest-looking form becomes the emptiest.
- **A gate, or somebody else's source** - `gate:` or `source:`, cited exactly.
- **A standard, a paper, a book** - `cited:`, naming the document and the
  section by name, so a reader reaches it without asking you. A standard kept
  in the tree may be cited by path as well.
- **Nothing, but it was measured** - `measured:`, naming what it was measured
  against and how, because that is what will make it stale.
- **Nothing, and it is judgement** - `judged:`. Allowed, and it will appear in
  every report as resting on nothing that re-runs. Not a reproach: that is the
  entry refusing to overstate itself.
- **Nothing at all, and you have not measured it** - then it is not a fact.
  Leave it in the queue and let the work be to obtain the provenance. If that
  work is a measurement, tag it `measurement` and name the claim in
  `known/status/` it defends - `check` refuses one that defends nothing, which
  is what keeps the queue from absorbing every question a measurement raises.

That last path is the ordinary case. A review once reported a fault of a known
class in a second place; nothing could demonstrate a wrong answer there, so it
stayed something to measure rather than a fault asserted. Copy that shape:
**weaken a claim as readily as you confirm it.**

And before adding, **search** for what is already there - `find` on the words
you were about to write, then `--near` whatever comes back closest. A subject
here is soon past reading end to end, and "I read the subject" stops being a
thing anybody does long before it stops being said.

Two entries saying one thing is how a reference starts disagreeing with itself:
cheap to prevent, expensive to find later, and invisible to `check`, which asks
whether a field is there and never what it says. When two turn out to be one,
merge them. When they are genuinely two, make the split visible **in the
titles** - two entries whose titles say the same thing are worse than a
duplicate, because a search returns both and neither says which to read.

## Picking work up

```
kb find --near 10
```

That is the entry whole, and a card for everything one link from it: where the
neighbour stands, which way the link runs, the sentence of its prose that cites
the entry, and the one field that decides whether to open it - a road put down
by its `because`, open work by its criterion, finished work by its outcome, a
fact or a rule by its title. The roads put down come first. Read them before
touching code: working without the refused alternatives is how a rejected
design gets proposed again with confidence. `--near` the neighbour whose card
bears on the task; `--full` prints every one whole.

**Under it comes a short list headed "what somebody else's software does".**
Those are measurements of the engine, the client, the kernel - the subjects
`project.md` names as `theirs` - that sit one
link *past* the working set, reached through a neighbour rather than through
the entry itself. They are there because the linking is done by hand and a fact
written today does not walk back into the entries it bears on: the behaviour a
task depends on may already be measured and written down, two links out, in
words the task would never have searched for.

Read one **before trusting a behaviour it is about**, not after. It is a handful
of lines and the whole point is that you do not yet know which of them you need.

**Shaped is not verified, and the first act is doubting the entry rather than
writing code.** It was shaped on the cases that were in hand, on a day that is
not today, and each of these is worth an hour before it is worth a week:

- **the premise** - does the fault still exist, and is it still where the entry
  says? Its cause is the part written from the fewest cases, so it is the part
  to doubt first;
- **the criterion** - is it still an observable, or is it stated against a
  quantity this work is about to move, in which case it stays true and checks
  nothing;
- **the reading of the code** - the entry describes a layer as it stood when it
  was written, and nothing has checked since.

The cheapest way to ask them all is the measurement the criterion should
already name - what the layer does over its whole population *today*, before a
line is written. That is also how an entry turns out not to be worth doing, and
`moot/` is a legitimate answer to picking one up: the queue can otherwise only
shrink through work, and a task whose premise has dissolved will sit there
looking like work.

**Taking many entries at once is when to ask it of all of them.** A scope, a
sprint or a release gathers entries shaped on different days, and the work
since has dissolved some premises and moved others. Hand each entry the scope
takes to a reader with the code in front of it, and have it report, entry by
entry, whether the premise holds, is overtaken, holds in part or needs a run to
tell - with the place it looked. Its verdicts are findings like any reviewer's:
check one against the code before acting on it, and an overtaken one before
closing it. Comparing the date an entry was last changed with the dates of the
files it cites does not ask this. Most commits to a file leave a given entry's
claim alone, so the comparison flags far more entries than it finds overtaken,
and it cannot see an entry that names no file.

Then work it in `scoped/`, moving it there first if it was not taken into the
scope already. `scoped/` is what was chosen to be done next, not the entry in
hand this hour; an entry that drops out of the scope unfinished goes back to
`analyzed/`.

## Closing it

Closing is its own piece of work, and it is not the same as finishing the code.
**Check twice that it is really done**: tests green, checks passing, nothing it
depended on left dangling, a second reader through it.

Write `outcome:` - what it reached, and the evidence, in the same forms a
provenance takes - with `kb set 10 outcome "…"`. Write it **before** you close:
that puts the demand at the moment the answer is still in your head.

Then `kb close 10`. It writes `closed:` with today's date and moves the file to
`done/`, and where `done/` would not hold the entry - no outcome, or one naming
no kind of evidence, a `quiet` mark still on it, a link that leads nowhere, or
a neighbour the move would leave broken - it says so and leaves the entry where
it was. A `mv` by hand skips all of that and the date with it.

**Groom it as you close it.** An entry worked in scope gathers dated notes, and
by the end its body says what was believed at the start while the notes say
what happened. Rewrite the body to what is true now - what was predicted, what
was measured, what was decided and why - and move the old text whole to
`kb/archive/` under `working:`. Do the same whenever a note overturns what the
body says. Notes that outgrow the body are debt: every `find --near` that
reaches the entry hands its reader the replay. `check` lists a shaped entry
carrying more dated notes than a closure ordinarily takes, and `kb` says how
many there are.

Between the outcome and the close there is a window, and `check` closes it: an
entry carrying an outcome and still sitting in the queue is listed at the end of every run. It
does not fail - holding one open while a second reader goes through it is the
ordinary case. Say **in the entry** what is holding it, and the listing becomes
a question with an answer instead of a nag.

A weak criterion shows up here, and that is the useful part: if there is nothing
to compare the outcome against, the criterion was never one. Notice it, and
write the next one better.

**Do not report a closure until somebody else has read the change.** A fix is
repeatedly right everywhere it reached and reaches fewer places than its own
description claimed - the code sound and the sentence about it not. Say
"narrowed" until then, and enumerate the sites: *"are there more?"* is a
question a second reader answers well and the author reliably fails to ask.

## Reviewing it afterwards

This is the after-action review (AAR), and when you are asked for one after a
long session, this is it. Once the change is committed and the work handed over - not at closing, which
has its own job - ask three questions and write down what they turn up:

- **what was predicted, and what happened?** The prediction is in the entry: its
  stated cause, its criterion, the shape the fix was expected to take. Where
  they differ, both are kept;
- **what would have been cheaper to know first?** Nearly always a measurement
  that was available before a line was written;
- **what generalises past this task?** If anything does, it is a guideline and
  is written as one.

What comes out is entries - `note` for what is still actionable, at most one in
`known/guidelines/` - and never a document, because a review written as prose
beside a live queue goes on reading as current. Nothing is the ordinary answer
and is said rather than left blank.

**Where a criterion was closed, point an adversarial tester at it first.** One
sentence and the population the work already produced - not the diff and not
the reasoning - and either a case where the claim is false comes back or a
statement that none was found over that population. Both go in the entry. A
criterion nobody attacked and a criterion that survived an attack read
identically once the file is closed.

## Ending it some other way

`moot/` - it stopped applying: superseded, dissolved, overtaken by what the code
became. `refused/` - it will not be done, because we declined it or because its
premise turned out false.

Both want `because` and `closed` - `kb set 10 because "…"`, then
`kb close 10 moot` - and both want the same double check: that
something genuinely **need not** be done is a claim about the world now, and it
deserves evidence like any other.

A **fact that turns out false** leaves `known/` for `refused/`, with `because`
saying what was believed, what is true, and how the error survived. It is never
left in place with a note calling it doubtful: a wrong measurement stated calmly
is worse than none, and a note does not make it safe. Moving it is not
annotating it - it leaves the live reference, and the record of the wrong belief
survives where it belongs.

A **superseded decision** goes to `moot/`, with `related` naming what replaced
it. The pair is the record; editing the old one would destroy what it exists to
preserve.

**Taking a refused route back out.** `refused/` is read at pickup and that is the
point of it - `find --near` returns those entries and prints the place beside
each. What must not follow is re-opening by having read one: the precondition is
that something moved which the `because` rested on, and *it might work now* is
not that. When something has, write a **new** entry for the route, `related:`
the refused one, and say in its body which clause of that `because` stopped
being true and what made it false. The old entry stays exactly where it is: it
was right on the day, and that is what the pair preserves. An idea taken out of
`refused/` with no entry behind it is the failure the store exists to prevent,
arriving by the one route the store cannot see.

## Cutting a settled entry down

When a measurement has produced a rule, the entry keeps **the rule**. Move the
investigation to `kb/archive/` and point `working:` at it.

This is the only thing that keeps the reference small, and it never feels
urgent. Do it when the rule stops being interesting - that is the signal it has
finished being an investigation and become a fact.

## Worth knowing

**Your own task list is not `scoped/`.** The task list is the working scope of a
*session* - hours, split however suits, then gone. `scoped/` is the scope of the
*project* - weeks, surviving sessions and agents. They may overlap or not, and
a divergence is not an error. Do not keep them in step.

**`check` does not judge.** It asks whether fields are there, never what they
say. Nothing will catch `criterion: fix it`, and nothing will notice that two
entries are one thing written twice. Content is yours.

**What the project itself owes the method is in its own instruction**, beside
the two commands that open a session: which tree is a release boundary, what a
change there costs, which documents decide. This file is the same in every
project, and says nothing about any of them.
