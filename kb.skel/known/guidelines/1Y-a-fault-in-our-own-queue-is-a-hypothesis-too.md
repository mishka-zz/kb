---
id: 1Y
title: A fault recorded in our own queue is a hypothesis exactly as a reviewer's finding is, and an old one more so
kind: fact
noted: 2026-08-28
tags: method, review, queue, carried
provenance: judged: three entries written from reading the code - one describing a quantisation the code prevents, one deriving a claim over a set nobody re-derived, one arguing that its own fault cost nothing - all three wrong in ways a measurement settled in an hour; and a fourth carrying a sentence about what had never run that a grep settled in a minute
related: 1B, 1R, 2B
---

[[1B]] says a reviewer's finding is a hypothesis and has to be checked before it
is written down as true. **The same holds for what is already written down**, and
an entry's age is not evidence: nothing re-reads it, so a fault stated from
reading the code stays exactly as sound as that reading was on the day.

**Where the line falls.** `known/` is what has been established, and its entries
carry a provenance saying how. Everywhere else - `noted/`, `analyzed/`, `done/`,
and the rest - an entry carries measurement and argument side by side and does
not mark which is which, so a sentence read out of one is a hypothesis whatever
it sounds like. The entry you are working is the exception only while you are
in it: what makes it safe is that you know which half is which, and that stops
being true the moment somebody else picks it up.

That is not a reason to strip the argument out. An entry that reasons about a
mechanism is worth more than one that only records a number - it is what tells
the next reader where to look. What it must not do is be read as settled.

Three shapes, each met on one entry:

**The mechanism does not exist.** An entry held that two quantities snap to
whatever nearby positions some earlier stage left, so their separation
quantises. They do not snap - the stage is asked for a position at each and pins
it - and the arithmetic downstream is invariant to where they sit anyway. The
entry was written by reading one layer and not the layer under it, and it was
read that way by everyone who opened it afterwards.

**The claim was derived over a set and never re-derived.** An entry said nothing
open returns a wrong answer on an input somebody is likely to send next. Two
entries written after it each say in their own bodies that their input is
ordinary. Nothing was inconsistent at the moment of writing; the record moved
underneath a sentence that was kept rather than computed.

**The argument was written in the voice of a finding.** An entry stated that the
seams it complained of cost nothing, on the ground that every one of them falls
where the structure already divides. It is a good argument and it is false: two
divisions of one input were run through and, where the division changed axis,
the results differed. Both sentences sat in the same paragraphs as measurements,
in the same voice, and would have gone into the product had the code been
written from the entry.

## What follows for how work is picked up

**Find out what the fault is worth before writing code for it.** Not as caution
- as the cheaper order. The first of those closed by measurement in about an
hour and needed no change to the product at all, and a fix written from its
description would have added a mechanism the stage below refuses.

The cheap angles come first and mostly need no long run: what does the code
actually do on the path the entry names, what does the arithmetic give for a
case whose answer is known, and what happens if you simply try the configuration
the entry describes. The last of those is the one most often skipped and is the
most informative - the attempt is refused, by a check nobody had connected to
the question.

**What rots is the premise, and it is the part nothing shows.** A `criterion:`
cannot say whether its entry is still alive: it is false for as long as the item
is open, and it is false in the same way whether the fault is real or the fault
has gone and the criterion was about something else. What separates those is the
present-tense sentence in the body saying what the code does *today* - "checked
by nobody", "resolved when the picker runs", "asks along one direction". That is
what goes false, and it goes false quietly, because a title and a criterion can
both survive it.

They are also the two things `kb.py` prints. The premises are in the body, which
the state screen never opens, and `stale` re-runs what `provenance:` and
`outcome:` cite - the established and the closed. So the record re-derives
everything except what is open.

**So re-read the premises before spending the queue, and not only when picking
one entry up.** The other trigger is the moment work starts; this one is the
moment a set of entries is about to be believed as a whole - a release bar, a
sweep's scope, a claim that nothing open contradicts something. An entry nobody
picks up still counts against a release, so a dead one holds it open at no
visible cost. The reading is cheap and needs nothing running.

**A measurement that says "nothing" is a result.** It costs a criterion's second
disjunct and it removes an item; what it must not do is quietly leave the entry
open because nothing was fixed. It also does not clear the question the entry
sat next to - closing the only candidate behind an open observation leaves that
observation with none.
