---
id: 3F
title: A message that tells the caller what to do is a claim about the code, and a test matching a word of it pins the half that is not the advice
kind: fact
noted: 2026-09-12
tags: testing, method, review, carried
provenance: judged: worked out on another record, where a layer wrote three
    refusals that went on to say what the caller should do instead, all three
    passed every review, and all three were false about how the code behaves
    under the thing they recommended - the code being right each time
related: 2V, 1B, 2B, 1E, 1S
---

A refusal that names what is wrong is a report. A refusal that goes on to say
what to do about it is a second claim, about how the code behaves under the
thing it is recommending - and nothing in a suite that matches a word of the
message touches that half.

The occasion it came from had three. One said no order between two overlapping
labels would settle their contest; an order settles it. One told a group that
ordering them would not help, when ordering was the only thing that did. One
promised that stating a neighbour would leave a label the rest, which the map
it is computed from cannot see. The code was right each time. What let each
sentence through is the shape of the assertion: the corpus pinned a refusal by
one word it must contain, and the unit tests pinned the clause that classifies
the input rather than the clause that tells the caller what to state. Both are
the natural way to write the check, and both are satisfied by advice that
contradicts the code beside it.

So where a message advises, assert the sentence whole - and where the advice
can be driven, drive it: do what the message recommends and check that what it
promised is what comes back. The second is cheap wherever the message is about
the layer's own behaviour.

The wider form is [[2V]]'s: an assertion written as ceremony is written
loosely, and a loose one is satisfied by whatever happens to make it true.
