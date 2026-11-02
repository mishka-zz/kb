---
id: 1B
title: A reviewer's finding is a hypothesis
kind: fact
noted: 2026-08-28
tags: method, review, carried
provenance: judged: a review reported a fault of a known class in a second place, and nothing could demonstrate a wrong answer there
related: 1Y, 2B, 1G
---

Check a finding before writing it down as true, and be as willing to weaken it
as to confirm it. The one above became something to measure rather than a fault
asserted.

The reviewer's best catch is usually **scope**, not correctness: repeatedly a
fix was right everywhere it reached and reached fewer places than its own
description claimed. The code was sound and the sentence about it was not. So
say "narrowed" until somebody else has read it, and report a closure last rather
than first.

**A narrowed condition is the part of a fix most worth having somebody else
read.** One entry stopped being a habit and became a much harder condition on
the day a review said what its fix actually reached - it covered one shape of
input and nothing more, so a neighbouring shape carrying the same fault was
still unreached. Nothing in the change was wrong; what was wrong was the
sentence describing which cases it now answers, and only a second reader asking
*"are there more?"* separates those two.
