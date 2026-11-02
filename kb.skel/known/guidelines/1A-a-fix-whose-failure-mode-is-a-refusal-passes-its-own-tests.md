---
id: 1A
title: A fix whose failure mode is a refusal passes its own tests
kind: fact
noted: 2026-08-28
tags: method, testing, carried
provenance: judged: three occasions, the clearest being a threshold set from a measured lower bound with no upper one ever looked for
related: 1E, 1B
---

A bound measured at one end is not measured. A value too small produced a
*decline* rather than a wrong answer, so every test passed while a supported
class of input silently lost its guard.

Measure both ends of a bound. And pick specimens by what could break the
mechanism, not by what the answers should be - a set covering kinds of *answer*
will not cover kinds of *failure*.

And before choosing any constant, ask whether the tree already answered the
question. In that case it had: the same figure stood elsewhere in the source for
the same reason, with its reasoning written out, one `grep` away.
