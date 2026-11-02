---
id: 3Q
title: A sweep varies the parameters as well as the inputs, or it cannot see the code that runs only when a feature of the input is near a parameter's scale
kind: fact
noted: 2026-09-12
tags: method, testing, carried
provenance: judged: worked out on another record, where a clean reader found
    faults in code a randomised sweep had just passed, and sweeping one setting
    over the same population reproduced each of them
related: 1F, 1T, 1E, 2B, 2N
---

A clean reader found faults in code a randomised sweep had just pronounced
clean. Each lived where a feature of the input is about the size of the
resolution the code works at. The sweep laid features many times larger than
that resolution, and could not have produced any of them.

**What the sweep was.** Random shapes on a lattice, each partitioned several
ways, every output compared against a reference computed from the whole shape.
It varied the inputs hard - the population was the point, and it had already
overturned a wrong answer once ([[1F]]). What it never varied was the resolution
setting. Every feature was many units across, so every branch that *declines* a
feature was unreachable.

**Where the faults were.** In the half of the arithmetic where a feature and the
resolution are comparable. That is not an exotic half. It is a common real case,
reached by anybody who asks for fine detail.

**What it costs to fix.** One variable. Sweeping the setting from well below the
lattice step to several times it took the same instrument and the same
population, and it is where the fixes were then confirmed.

**And the oracle has to be free of the setting.** The first version applied the
setting inside the reference, so it agreed with the code about how the setting
applies by making the same assumptions. Split it: the reference answers what the
input is, the comparison applies the setting, and a disagreement about the
setting has somewhere to show. [[1T]] is the same rule about an instrument's
blind spot; this is where the blind spot is a *parameter* rather than an input.

**Watch for the answer that is deliberate.** Push the setting far enough and
many outputs take a documented fallback. That is a rule doing its job, and an
instrument reading it as a fault would be measuring the fallback instead of the
thing under test. Teach the comparison the deliberate outcomes, or the sweep's
own noise floor rises until it hides what it was built to find.
