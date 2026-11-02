---
id: 2N
title: A sweep that comes back flat has found a bound and cannot say which bound, so it has to reach past where it meant to stop
kind: fact
noted: 2026-09-12
tags: method, testing, convergence, carried
provenance: judged: worked out on another record, where a sweep over more than
    two orders of a parameter got one identical answer at every point and was
    written up as the platform ignoring the request; one step past where it
    stopped the answer moved, and kept moving for three orders more
related: 1T, 1A, 1F, 2X
---

A response that does not move over the whole range swept looks like a floor and
is only a bound. Something is holding the answer; the sweep says nothing about
*what*, and in particular nothing about whether the thing holding it is the one
being varied.

That record's case read as a property of the platform and was written down as
one. The band was two and a half orders wide. One step below where that sweep
stopped, the answer moved. What held the band turned out to be a *second*
criterion the caller was not varying, and the entry built on top of that
reading had its premise inverted.

**So a sweep whose point is a limit has one more obligation than a sweep whose
point is a rate.** It has to reach a place where the answer moves again - and
where it does not, say so in the entry, because "flat everywhere I looked" and
"flat" are different claims and only the first one was measured.

The cheap version of that obligation: extend by an order and look, before
writing the conclusion rather than after. Both ends, since a plateau has two -
[[1A]] is the same demand made of a bound measured once.

It is [[1T]]'s fault in another parameter: a sweep that finds nothing has
measured the instrument, and here the instrument was the range chosen before
anybody knew what it had to cover.
