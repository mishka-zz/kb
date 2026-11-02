---
id: 3W
title: A specimen kept clear of coincidences is the one input users do not make - they write round numbers and symmetric layouts, and a derived point then lands exactly on a boundary
kind: fact
noted: 2026-09-13
tags: method, testing, carried
provenance: judged: one occasion on another record, where a corpus placed its
    one small item off the middle on purpose and an adversarial tester's layout
    in round numbers was refused
related: 1A, 2B
---

A corpus specimen is often placed where nothing lines up, so that the case it is
about is the only thing in it. The inputs people make are the opposite: whole
numbers, symmetric layouts, parts centred on each other. A quantity the code
derives from the input - a centre, the middle of a range, the edge of a region -
then lands exactly on another part's boundary, and any test of containment
answers for both at once.

**The occasion.** On the record it came from a corpus placed a small item off the
middle of its region, its comment saying why: so that nothing of it fell on a
point the region is symmetric about. Every version of a check passed that
corpus. An adversarial tester laid out an L-shaped item in round numbers, and
the check refused it: at those proportions the L's centre fell exactly on an
edge it shared with its neighbour, and the library answering containment counts
a point on a boundary as inside both.

**What to do.** Put the coincident case beside the clean one: the part at the
middle, the dimensions in round numbers, one thing centred on another. Where the
code derives a point from the input, ask where that point lands in the inputs
people make, and put a specimen there. It is [[1A]]'s rule applied to position:
pick specimens by what could break the mechanism, and the mechanism here is a
point on a boundary.
