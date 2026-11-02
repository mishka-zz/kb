---
id: 1W
title: A change that makes a relationship exact disarms every assertion that was checking it, so re-read them as part of the change
kind: fact
noted: 2026-08-31
tags: method, testing, review, carried
provenance: judged: worked out on another record, where a change made a grid
    edge exact by construction and three assertions about that edge stopped being
    able to fail, every one of them found by a reviewer rather than by the suite
related: 1S, 1E, 1X, 1A
---

A change that turns an approximate relationship into an exact one is the change
most likely to leave a test passing for a reason that has nothing to do with its
name. The assertion still reads correctly, still describes something true, and
can no longer distinguish a working code path from a deleted one.

[[1S]] is the neighbouring fault and its tell does not catch this one. There the
assertion is pinned to a quantity the work is about to move, and the number
moves with the code. Here the assertion names no number at all: it states a
relationship, the work makes that relationship hold **by construction**, and
what was a check becomes a restatement of the new design.

**The tell is the phrase used to describe the improvement.** *By construction*,
*algebraically*, *exactly*, *cannot happen any more*, *any order gives the same
result* - each says some quantity has stopped varying, and every assertion about
that quantity has stopped being an experiment.

**The variant to watch for is a whole path going inert.** A test written *for*
the defect it fences can stop reaching it, because the work moved the code it
measured out of the rule's reach. That is worse than a stale assertion, since
the test's shape is exactly right.

**What to do is ask the question, not run the suite.** A green run is evidence
of nothing here, by construction - every one of them was green. After a change
of this kind, take the assertions near the quantity that stopped varying and ask
of each what source line it is now sensitive to, then break that line and check.
Where the answer is *none*, the assertion moves from the consequence to the
rule: not "the output did not move", but "the input carries no such part".
