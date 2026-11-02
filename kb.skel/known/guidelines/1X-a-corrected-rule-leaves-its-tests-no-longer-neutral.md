---
id: 1X
title: Correcting a rule leaves its tests no longer neutral, and the ones that stop failing say as much as the ones that start
kind: fact
noted: 2026-08-28
tags: method, testing, review, carried
provenance: judged: a corrected rule left a class of twenty specimens - every one built to make the old rule bite - silently exercising nothing, which read as a broken fixture rather than as a finding
related: 1E, 1S, 1B
---

A fixture is not drawn at random. Its specimens are chosen so that the rule
under test *does something* to them - an input that crosses a boundary, a value
that falls between two cases, an offset that moves an answer. That choice is
what makes the fixture sharp, and it is also what ties it to the rule as the
rule stood.

So when the rule is corrected, the fixture stops being an independent witness.
Its specimens now sit wherever the *old* rule needed them, which under the new
one may be nowhere in particular.

**Read the tests that stop failing.** A test that starts failing is loud and
gets attention. A test that quietly starts passing - or that still passes while
no longer distinguishing anything - is the same evidence with the alarm removed.
Twenty specimens turned green in one edit, and the reason was not that the code
got better: every one of them had been constructed to sit exactly where the old
reading put the boundary, and under the corrected rule they arrive unremarkable.
The class had been measuring an artefact of the reading it was written under.

**The two failure shapes are opposite and both arrive at once.** Half the class
went green because the corrected rule made its specimens uninteresting; the
other half failed on figures the old rule had produced. It is tempting to treat
the first half as relief and only work on the second. The first half is the
finding.

**What to do.** After correcting a rule, re-derive what the fixture was for:
state in one sentence what property of a specimen made the old rule act on it,
work out the corresponding property under the new rule, and rebuild the
specimens on that. Adjusting the old numbers until the tests pass again keeps a
class that can no longer fail.
