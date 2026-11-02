---
id: 2M
title: An agent maintaining a record fails by dropping what it did not mention, so an update edits a field and never regenerates the entry
kind: fact
noted: 2026-08-29
tags: method, record, carried
provenance: cited: Badhe, Tiwari and Chung, SKILL.state - Scalable Long-Horizon Agent
    Skills, arXiv 2608.26263v1, 2026-08-26, section 5.7 error taxonomy
related: 1N, 1P, 2K, 1V
---

Measured on an open-weight model asked to maintain a structured execution state
across a long run, the failures sort into three kinds, and **68% of them are the
model omitting keys that already existed** - overwriting the record instead of
merging into it. Another 20% are schema confusion and 12% malformed syntax. None
of the three is a reasoning error. The authors' own reading is that the
degradation "stems from structured output adherence rather than reasoning
capacity".

A second, independent observation of the same shape: in Tang et al., WikiSkill
(arXiv 2608.27454v1, 2026-08-27, table 4), the wiki-maintaining agent is
instructed that pattern pages should be 10-30 lines, and the pages it produces
average 18.1 to 48.2 lines depending on the model - it runs past its own stated
bound without anything noticing. Different failure, same class: an unattended
writer drifts, and the drift is silent.

**So the refusal. An update to an entry edits the field that changed.** Do not
hand a whole file back through a model and let it re-emit the rest from memory:
what it does not happen to mention is gone, and the diff will not look like a
deletion because the file was rewritten whole. This is the one edit shape whose
failure leaves no trace to catch.

**It is also why three things here are built the way they are.** `check` is
mechanical and asks only whether a field is *there*, because that is exactly the
class of loss above. State is the directory and no field holds a copy, so a `mv`
cannot silently take the other fields with it. And [[2K]] keeps the owner's
audit, because a self-review is run by the same writer that drops things.

**What this does not say.** Neither measurement is from this codebase, and
neither is about an agent writing prose entries - both concern structured state
under a schema. What carries is the class of failure, not its rate.
