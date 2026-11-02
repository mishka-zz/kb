---
id: 3K
title: A finding worth re-reading is usually about something other than the case that raised it, so ask what else it could be before calling it a defect
kind: fact
noted: 2026-09-12
tags: method, review, carried
provenance: judged: worked out on another record, from findings of its manual
    test sessions that each turned out to be about something other than the
    case that raised them
related: 1K, 1M, 1B
---

The findings worth re-reading are not the ones that were what they looked like.
They come in recognisable shapes:

- **The program was right and the step was wrong.** A guard written from the
  finding's own reasoning would have refused a case already shipped and known to
  be correct. This is the dangerous shape: acting on it looks like fixing a bug
  and actually breaks a correct case, and the sweep would have reported a pass
  afterwards.
- **The inconsistency was already documented, on one side of it.** A check
  defined a term in its own docstring and the step it fed did not, so a green
  check certified an input the later step then got wrong. What the sweep found
  was a disagreement between two files, and only one of them was written down.
- **A docstring settled it.** Two parts of the system disagreed about a number,
  and the criterion in somebody's docstring said which was right. No measurement
  was needed, and no argument either.

So when a finding does not resolve cleanly, ask what *else* it could be about
before writing it up as a defect - the code being right, two documents
disagreeing, or a definition nobody wrote down twice. That is [[1B]] applied at
the moment of writing rather than at the moment of fixing, and [[1K]] is why the
question is asked before anything is repaired.
