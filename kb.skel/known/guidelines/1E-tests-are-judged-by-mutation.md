---
id: 1E
title: Tests are judged by mutation, and a measured quantity is asserted with tolerances rather than as a bit-for-bit snapshot
kind: decision
noted: 2026-08-28
tags: method, testing, carried
because: Coverage does not distinguish a test that asserts from one that merely executes, so it can only ever say a line ran. Breaking a source line and checking that something fails is the one measurement that separates the two. And a snapshot of a computed number tests the number rather than the behaviour - it fails on a legitimate change and passes on a wrong one that happens to land on the same value.
related: 1A, 1S, 1X
---

Break a source line and check something fails. That is the whole of it, and it
is the reason no assertion is pinned to an incidental figure: assert the
property instead - that what was reserved equals what was laid, that two routes
to one answer agree, that a count does not move when the irrelevant thing
changes, that the answer is inside the reference's own accuracy.

A measured quantity is asserted with **tolerances**, never as a bit-for-bit
snapshot. A snapshot comparison belongs on a serialised interface and nowhere
else, that being a place whose exact bytes genuinely are the contract.

A fix whose failure mode is a refusal passes its own tests ([[1A]]), so pick
specimens by what could break the mechanism rather than by what the answers
should be.
