---
id: 2A
title: Before re-running a gate to show a change did not move it, ask whether the run can differ at all - the proof is exact where a re-run is only within tolerance
kind: fact
noted: 2026-09-12
tags: method, gates, testing, carried
provenance: judged: worked out on another record, where a change to the rule
    placing a structure's faces settled every gate over that structure in minutes
    by drawing what the evaluation is handed before and after and diffing the two
    trees - all identical - where re-running the gates would have taken hours and
    answered a weaker question
related: 1E, 1G, 1W, 1K
---

The reflex after changing anything a slow evaluation is handed is to run the
gates and see whether a figure moved. That is hours, and it answers a weaker
question than it looks: a gate passes inside its reference's own accuracy, so
"it still passes" does not say the number stayed put, and "the number moved a
little" does not say which change moved it.

**Ask instead whether the run can differ at all.** An evaluation is a function
of what it is handed, and what it is handed is usually cheap to produce and to
compare byte for byte. Produce it with the change and again without, and diff.
Identical on every input and no evaluation can differ - which is an exact
answer, not one within a tolerance, and it holds for every case the producer
covers rather than for the operating point a gate happens to run.

It also says *where* to look when it fails. A diff that shows one input's
representation moving names the input and the field, which a moved figure never
does.

**What it does not settle** is a change to anything downstream of what was
compared - what the model does with it, how the result is read, what a gate
computes before it asserts. There the run is the measurement and there is no
shortcut. And a green diff is not a green gate: it says nothing moved, so it is
worth having only where the gates were green before. [[1G]] is the rule that
makes the diff honest - it is against the old build run for real, not against
the new one patched to behave.
