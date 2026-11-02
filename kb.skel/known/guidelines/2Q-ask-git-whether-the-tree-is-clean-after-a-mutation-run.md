---
id: 2Q
title: Ask git whether the tree is clean after a mutation run - an interrupted one leaves its mutant on disk, and a shell trap does not reliably undo it
kind: fact
noted: 2026-09-12
tags: testing, method, tooling, carried
provenance: judged: worked out on another record, twice in one session - a
    mutation loop killed mid-pytest by a two-minute harness timeout, once with no
    trap and once with a trap on EXIT, INT and TERM that did not fire; both left
    the mutated source in the tree, found only when a later anchor stopped
    matching
related: 1C, 1E, 1B, 3C
---

[[1C]] is one way a mutation you believe you reverted is still there: the
bytecode cache holds it. This is the other, and it is cruder - the source itself
was never put back, because the loop that would have put it back was killed.

Anything that stops the run between the write and the restore does it: a
harness timeout, a cancelled command, a machine that ran out of patience. A
shell `trap` on `EXIT INT TERM` reads like the answer and is not one; it did not
fire on either occasion.

**What it costs is worse than [[1C]]'s.** A stale cache gives a false
*survived*, which reads as a missing test. This gives a **live mutant in the
working tree**, so everything measured afterwards is about code nobody wrote -
and the next mutation's anchor fails to match, which reads as the source having
moved rather than as the source being wrong. [[3C]] is what a clean reader
launched over such a tree reports.

**The guard is one question and it is cheap.** After any mutation run, ask git
whether the tree is clean before believing anything the run said. And run the
loop detached rather than in the foreground, so a caller's timeout does not
reach it.

The tell that something has gone this way: an anchor that reports zero matches
on a line that is plainly in the file.
