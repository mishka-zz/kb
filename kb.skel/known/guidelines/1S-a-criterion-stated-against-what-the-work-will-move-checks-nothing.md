---
id: 1S
title: A criterion stated against a quantity the work is going to move stays true and checks nothing
kind: fact
noted: 2026-08-28
tags: method, criterion, testing, carried
provenance: judged: an entry's criterion was written against a step size and the fix changed the step, so it read as satisfied by a different case than the one it was written about
related: 1E, 1H, 1X
---

The entry asked that *a feature narrower than one step be measured as the thing
it is*. The fix was to change the step. The sentence came out the far side still
true and about a different feature, so at closing there was nothing to hold the
work against - and a criterion whose whole job is to be held against the work
had quietly stopped having one.

**The tell is that the criterion names one of the work's own knobs.** A
criterion is admissible when the thing it measures is fixed by the input, by the
standard, or by the user - a declared count, a corpus, a closed form - and
inadmissible when it is fixed by the code the work is about to rewrite. Both
read the same on the way in; only one still says something on the way out.

**Same fault one level down, in assertions.** A figure taken from the constant
under test moves with it and asserts nothing about where the constant belongs.
The other direction costs too: an assertion asking for a tolerance far tighter
than the module promises, held by where some search happened to start, fails the
moment that starting point moves. An assertion pinned to something nobody
declared fails on a legitimate change and passes on a wrong one.

**How to write it instead.** Say what the input gets: *a record split across
folded lines yields the same fields a flat one yields*. That is the same
intention with nothing of the implementation in it, it can be checked at
closing, and it survives the next change to how the work is done.

## The mechanical tell, because knowing the rule is not enough

This was written down, and an hour later a test went in asserting that two
events `10 * SAME_EVENT` apart are two events. It passes at every value of that
constant, including ones a hundred times too large, because the case moves with
the number. The rule had been read; it did not fire, because a tolerance scaled
by its own constant reads like care rather than like the fault.

So do not rely on noticing. **Change the constant and re-run.** A test that is
about a constant fails when it moves; one that survives is about the structure
and says nothing. Both ends, and both from a quantity that is not the constant.
