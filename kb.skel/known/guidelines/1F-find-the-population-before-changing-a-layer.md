---
id: 1F
title: Before changing a layer, find the population it runs over and what gets read off it - a structure nobody drew and a property nobody asks about hide the same way
kind: fact
noted: 2026-08-31
tags: method, coverage, testing, carried
provenance: judged: worked out on another record, where two faults of different
    kinds surfaced on the first structure class nobody had drawn before, neither
    reachable on any example that shipped; and where a population large enough
    to reach a cost fault ran it on every pass and hid it anyway, nothing being
    read off the run but whether the answer was right
related: 1S, 1Y, 1E, 2S, 2Z
---

A corpus covering kinds of *answer* does not cover kinds of *structure*. A fault
that needs a structure nobody has drawn is not rare - it is **unobserved**, which
is a different thing and reads identically from inside a green suite.

So the example set is a test surface, not a gallery, and what is missing from it
reads off the list of structure classes the component claims to handle, never off
what has failed so far.

**Which makes the first question about any change a question about population:**
what is the set this layer is defined over, and where is that set *executed*? A
layer with such a set meets the cases nobody remembered, every time it is
touched. A layer with no such set has no coverage to speak of, however many tests
name its cases one at a time - and building the set is the work to do first,
rather than the risk to accept.

## And the population is only half of it

A layer can have its population and run it on every pass and still hide a
fault, when every assertion over that population asks one kind of question.
The record it came from's case was a quadratic that had run inside the suite for
weeks: the answers were right, so nothing complained, and the cost was never
read off the run.

**What hid it is that the suite reads one property off its population.** A
phase can be right and unaffordable, and there is nothing in a population,
however large, that makes that visible on its own - the run has to be read for
it. So the opening question gets a second half. *What is the set this layer is
defined over, and where is that set executed?* stands. Add: **and what is read
off it when it runs?** A corpus executed by property tests that all ask one kind
of question covers one kind of question, and its size is no argument against
that. The classes of fault are as much a listing as the classes of structure.

The instrument that came out of it is worth copying: a value each phase hands
back saying what it spent, held to how it grows rather than to a figure. It
found something on the day it was written, which is what says the reading was
missing rather than merely thin.
