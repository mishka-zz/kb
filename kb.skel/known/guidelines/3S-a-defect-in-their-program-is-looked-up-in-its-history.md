---
id: 3S
title: A defect found in somebody else's program is looked up in that program's later history before anything is built around it
kind: fact
noted: 2026-09-12
tags: method, carried
provenance: judged: worked out on another record, where a defect measured in
    an external program had been fixed upstream weeks before and released days
    before, while the workaround on the table would have written it into a
    shared layer of ours
related: 2Y, 2C, 3J
---

A program somebody else maintains keeps being fixed after the copy here was
built. A fault found in it today may already be fixed in their tree, and
whether it is costs one look: the log of the file the fault lives in, and the
changelog of the release after the one installed.

Look there before designing anything around the fault. A workaround built first
lives in our code after the reason for it is gone. It is also written where the
other program's defect does not belong. On the occasion it came from the proposal
was to change every file a shared layer writes, so that an old release of one
consumer would read them correctly - in a layer that serves every consumer and
belongs to none.

**The shape of the occasion.** The behaviour was measured first, with the reason
for it recorded as not established. The mechanism was then found in the other
program's source, and the log of that one function showed the fix, already in a
release. The fix on our side became a version floor - the older release refused
by name - rather than a change to the shared layer.

[[2C]] is the wider rule, asking the platform before blaming it, and [[2Y]] says
which channel answers what a release contains.
