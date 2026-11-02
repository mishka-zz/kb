---
id: 1P
title: A document that describes behaviour is checked against the code every time it is touched
kind: fact
noted: 2026-08-28
tags: method, documentation, record, carried
provenance: judged: a round of corrections whose findings were mostly documents describing a codebase that had moved underneath them
related: 1N, 1J, 1B, 2M
---

Not "reviewed periodically" - checked on the edit, by whoever is making it, on
the paragraphs around the one being changed. The cost is minutes and it is paid
by somebody who already has the file open.

The reason it has to be an edit-time rule is the failure mode. A document
describing behaviour does not decay evenly: the code moves under one paragraph
while the rest stays true, so the file goes on reading as correct and nothing
about it looks stale. Most of what a document-correcting round turns up is that
- prose that was right when written, sitting beside prose that still is.

Nothing re-runs prose. A test that cites a behaviour fails when the behaviour
moves; a sentence describing the same behaviour does not, and a reader has no
way to tell which of the two they are looking at. The edit is the one moment
somebody is guaranteed to be reading both.

**Stale description is not merely inert - it wins against the truth in front of
it.** Badhe, Tiwari and Chung, *SKILL.state*, arXiv 2608.26263v1, 2026-08-26,
section 5.4, change the world underneath a running agent and count how long it
takes to notice. Where the past is carried as accumulated description, the agent
contradicts the new observation for **five to eight consecutive steps** - the
authors' reading is that the obsolete facts overpower it - against zero steps
where the past is carried as current state. So the cost of a stale paragraph is
not the paragraph; it is the correct reading that gets argued down by it, which
is why this cannot be left to a later sweep.

**What that does not establish.** It measures an agent's context, not a
document, and it says nothing about *when* to check - the edit-time rule is ours
and rests on the occasion in the provenance. What it supplies is the size of the
harm, which was the part held on judgement.
