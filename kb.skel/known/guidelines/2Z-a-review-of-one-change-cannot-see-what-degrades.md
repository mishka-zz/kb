---
id: 2Z
title: A review of one change cannot see what degrades between changes, so that class is found by a pass over the whole tree and the occasion for it is the release
kind: fact
noted: 2026-09-12
tags: method, review, quality, release, carried
provenance: judged: worked out on another record, where a reading of the whole
    tree by readers carrying nothing from the sessions found faults that no
    review of the change that caused each could have seen, and a second pass of
    the same shape over the prose found statements the code contradicts in a
    user manual and in the project's own architecture document
related: 2B, 2T, 1P, 1H, 1B, 2C, 1F
---

A release holds its scope, and holding it is right. What the scope does not
cover still moves, and some of what it moves is invisible at the moment it
moves.

**Every rule this record writes down is applied to a change**, by somebody
carrying the session that produced it. That leaves a class neither the rules
nor a careful author can reach:

* a duplicate whose twin is in a file the change did not open;
* a comment that was true when written and stopped being true when a different
  file changed - the change that broke it does not contain it;
* a module that grew past its subject one defensible commit at a time;
* a public name that lost its last consumer somewhere else;
* a claim stated calmly that nothing re-derives, read back later as measured;
* a cost that reads correctly line by line and is a fault only over the
  population it runs on - [[1F]]'s second half.

Each of these is created correctly, or becomes wrong later, or is wrong in a
file nobody had reason to open. A review of the change is looking in the wrong
place, and looking harder does not help.

**So the pass is over the whole tree, and its occasion is the release.** There
is no other regular occasion. Readers carrying nothing from the sessions, one
per region, each finding checked against the code before it is acted on
([[1B]]). What the procedure must not do is restate a check that already runs:
a sweep with no judgement in it belongs in a test, where it fails continuously.

**A prose pass finds the same class in a different material.** A rule arrives,
and the sentences written before it are not re-read: a capability note promises
what a report elsewhere denies, a document attributes a check to a layer that
never makes it. Two things separate that pass from a code one. Nothing runs
over prose ([[2T]]), so a clean reader is the whole instrument and has to be
told to open the code under every sentence rather than to judge the sentence.
And a reader will report a finding that is false, so each costs a grep.

What the pass does *not* find is as much the point: whatever a test already
holds comes back clean, which is what [[1H]] buys. Everything that drifts is in
the half nothing runs over.
