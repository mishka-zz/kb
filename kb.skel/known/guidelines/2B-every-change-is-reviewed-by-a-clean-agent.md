---
id: 2B
title: A change is measured, discussed where it moves a gate, tested by mutation, read by a clean agent, and then its claim handed to an adversarial tester
kind: fact
noted: 2026-08-28
tags: method, review, workflow, carried
provenance: judged: kept as the loop for a piece of work on another record, where
    it caught a wrong criterion and a wrong justification under a constant, and
    where its clean review later found a false claim on the interface of a gated
    test while its adversarial tester found the claim false over a population the
    test never looks at
related: 1B, 1Y, 1Z, 1E, 1K, 1X, 2K, 3C, 3D, 3E, 1R, 1T
---

The loop for a piece of work, in order:

**Measure what the fault is worth**, before writing anything for it - [[1Y]]
says why that is the cheaper order and not merely the careful one.

**Discuss it with an agent** where the change will move a number a gate scores.
Brief it with the measurements rather than the conclusions, and ask it to attack
the reasoning rather than confirm the result. The brief also carries what earlier
work on the subject already settled as an invariant, and asks that every
threshold in the design be derived with its margin stated ([[1Z]]). And it asks
for a pre-mortem: what would a clean reader find wrong in this design? A design
agent that answers that before reporting spares a whole round of reader, fix and
mutation afterwards. On the record it came from the reader's main findings on one
piece of work were both of those kinds - a rate taken from the continuous model
where the earlier work had settled that the discrete one's is the one that
holds, and a threshold with no margin - and both cost that round.

**Implement, then make it work with tests**, judged by mutation ([[1E]]). The
boundaries a mutant will find are visible while the code is written, so their
tests are written with it: an empty input, the top of a range and exactly on a
boundary, a sign that is free, a value that is not a number in each input, an
extreme taken over a sum against one taken over a part. On that same piece of
work three mutation rounds found little else, each one a round of agent, test
and re-check.

**Then a review by a clean agent** - a fresh one carrying nothing from the
session, given the diff and the surrounding code and told not to modify
anything. What it is for is the half a session cannot see about itself: the
session knows what it meant, and a reader who was not there knows only what is
written. [[3C]] is the one condition on the step: the reader reads the working
tree, so nothing else may be writing to it while it does.

A review's findings are hypotheses like any other ([[1B]]), and the ones worth
most are usually about scope and about the reasoning underneath a result rather
than about the result.

**Then an adversarial tester, where the change claims something** - one agent,
one sentence to refute, the population and not the diff. It is a step after the
review and never in place of it, and launched after the reader's fixes rather
than beside the reader, since the fixes are what it has to attack.

**What the two read is not the same.** A reviewer works over the diff and the
code around it and is looking for anything wrong. An adversarial tester is given
one sentence and is looking for a case where that sentence is false. Merging the
roles does not buy a reading that is both; it buys the narrow one, with the wide
one skimmed - and the general faults are most of what a review is for.

**What the adversarial tester is given** is the claim in one sentence and the
population already in hand - the corpus, the generator, the measurements the
work produced. Not the diff and not the reasoning: an agent given the argument
attacks the argument, and the argument is not what has to survive. **What it
returns** is a case where the claim is false, or a statement that it worked over
that population and found none. The second is a result and is written into the
entry: *attacked and held* is worth more than never attacked, and the two are
otherwise indistinguishable in a closed file.

**When to spend it.** Where a criterion is about to be closed, where a fact is
about to enter `known/` on this session's own measurement - a generalisation
over the cases the session happened to see, which is [[1R]]'s subject arriving
one place earlier - where a number carries a story ([[1Z]]), and where a rule
was corrected and its fixture may no longer bite. Not on every change: an
adversarial tester on a change that claims nothing has nothing to do, and
running one anyway teaches the loop that the step is ceremonial.

**And its silence is not a clearance.** It is one more instrument, held to
[[1T]] like the rest: an adversarial tester that finds nothing over a population
that could not have produced the case has reported on the population. Where
a claim is about what somebody else's software does, it needs a specimen rather
than an argument; where it cannot produce one it says so, and the claim stands
exactly as strong as its measurement.

**Afterwards, once it is committed**, the work is reviewed for what it taught,
which is [[2K]] and is deliberately not part of this loop: closing is urgent,
and a question asked beside an urgent one loses.
