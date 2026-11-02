---
id: 1K
title: Confirm, do not fix - a repair made during a sweep destroys the measurement and changes what the later steps test
kind: fact
noted: 2026-08-28
tags: method, qa, testing, carried
provenance: judged: a sweep run under this rule end to end, with every defect it raised fixed afterwards as its own piece of work
related: 1M, 1N, 1B
---

A sweep is a measurement of one build. Fixing something in the middle of it
means the steps before and the steps after were run against different code, and
neither the pass nor the fail afterwards says what it looks like it says. The
tempting case is the one-line fix, which is exactly the one that gets made
without stopping to think about what it moves underneath.

So findings leave the session, and the fixing is the next piece of work. That
also gets the ordering right for [[1B]]: a finding is a hypothesis, and a sweep
is the wrong moment to test it - the sweep's job is to record it faithfully.

The cost is a second pass over the same ground, and it is worth paying. The
benefit is that the transcript is a single measurement of a single build, which
is the only thing it could have been useful as.
