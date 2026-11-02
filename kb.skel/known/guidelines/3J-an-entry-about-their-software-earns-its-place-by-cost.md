---
id: 3J
title: An entry earns its place in a reference about somebody else's software by having cost somebody a debugging session
kind: fact
noted: 2026-09-12
tags: method, record, carried
provenance: judged: worked out on another record, as the admission bar kept by
    its reference on an external program it drives, before and after that
    reference moved into the record
related: 1P, 1N, 2C
---

The bar for admission is not "true" and not "interesting". It is **that somebody
lost time to it**. A record of everything true about an external system is that
system's source code, and there is already a copy of it. A record of the things
that cost a session is short enough to read, and it is the thing that pays: the
next contributor arrives with the *symptom* and needs to reach the mechanism
from it.

These entries live under the subjects `project.md` names as `theirs`. Each
carries the same three things, under the schema's fields:

- **The symptom**, in the title and the opening lines - what it looks like,
  including the test or the workflow that surfaced it. This is the part somebody
  searches for, so write it in the words a person has in front of them, not in
  the words they have after understanding it.
- **The mechanism**, cited in the other project's source as a `source:`
  provenance. Without it the entry is folklore, and a later reader is entitled
  to overrule folklore.
- **The guard** - the defensive measure in our code that has to stay. Name it,
  so that a refactor removing it is visible as removing it. A guard nobody can
  find comes out in the next tidy-up, and the bug returns with it.

The guard is the part that makes the record act on the code rather than merely
describe it, and it is the one most often left off.
