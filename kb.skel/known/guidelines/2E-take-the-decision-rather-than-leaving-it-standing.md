---
id: 2E
title: Take the decision rather than leaving it standing for somebody else
kind: fact
noted: 2026-08-28
tags: method, conventions, design, carried
provenance: judged: a hedge written beside a value that disagrees with its name leaves the reader to settle which is meant, and a feature built from several mechanisms at once leaves nobody able to decline one of them
related: 2D, 1V
---

**A discrepancy is fixed, not annotated.** No notes to the reader in code, in a
data file, or in anything the user sees. A hedge beside a value that disagrees
with its name - a figure "nearer" some other figure, a comparison with something
not in front of the reader - leaves the disagreement standing and hands it to
whoever reads next. Change the name, or change the number, so the two agree.
Where neither can change, the disagreement is a fault and belongs in the queue
rather than in a parenthesis ([[1V]]).

**A scope is offered, not arrived at.** Build the smallest thing that answers
the question. Where a feature genuinely needs several mechanisms working
together, say so before building it and name the version that drops the least
valuable of them. The cost of getting this wrong is not the extra code: several
mechanisms shipped together are several decisions taken at once, and none of
them can be declined afterwards without the rest coming apart.
