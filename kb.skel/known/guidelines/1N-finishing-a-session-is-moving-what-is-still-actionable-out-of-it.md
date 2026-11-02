---
id: 1N
title: Finishing a session means moving everything still actionable out of it first; the transcript becomes a record that same day
kind: fact
noted: 2026-08-28
tags: method, qa, record, carried
provenance: judged: a folder of finished transcripts left sitting beside a live plan, and read as current until it was moved
related: 1K, 1V, 2M
---

A transcript is live for exactly as long as the session is running. The day it
finishes it is a record - evidence of what one build did on one day, never an
instruction.

The move is not the whole of finishing, though. **Anything still actionable in
it goes onto the open list first**, and that transfer *is* what finishing means:
until it has happened, the transcript is the only place a live fault is written
down, and archiving it then buries the fault rather than filing it. Do them as
one act, in that order.

What makes this worth a rule rather than a habit is what the alternative looks
like. Finished transcripts left beside a live plan do not read as history; they
read as current, and a reader acts on a number in one of them that stopped being
true. Length is what does it - nobody checks the date on the eleventh page.

**Two outside measurements land on the half of this that is general** - that the
transcript is scaffolding and the structured record is the artifact.

- Badhe, Tiwari and Chung, *SKILL.state*, arXiv 2608.26263v1, 2026-08-26,
  section 5.6. Their budget-matched control is the useful part: at one fixed
  prompt budget, a sliding window scores 0.18, statistical compression 0.22, a
  running summary 0.52, and a structured state 0.94 - against 0.84 for the
  unbounded transcript it replaced. **Shortening the record bought nothing;
  structuring it beat even keeping everything.** A summary of a session is the
  0.52 option.
- Tang et al., *WikiSkill*, arXiv 2608.27454v1, 2026-08-27, section 3.1. Raw
  traces are kept but never read by the agent doing the work; only the
  consolidated record is. Same division, reached for a different reason.

**What they do not establish.** Both concern agent runtimes, not a person
reading a folder, and neither has an analogue of the open list - so the transfer
half of this rule, which is the half that makes it more than archiving, rests on
the occasion above and on nothing else. They also say nothing about *when*: the
same-day timing here is ours.
