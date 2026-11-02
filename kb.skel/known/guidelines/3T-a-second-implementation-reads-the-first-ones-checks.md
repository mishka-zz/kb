---
id: 3T
title: When a second implementation takes on something the first already does, the first one's checks on it are read before the second is designed
kind: fact
noted: 2026-09-12
tags: method, review, carried
provenance: judged: worked out on another record, where a second backend's
    check on an input was built to ask one end of a range, and an adversarial
    tester found an input invalid at the other end handled without a word - a
    case the first backend's validation had answered all along, at both ends
related: 1F, 2B, 3H
---

An input means the same thing to both implementations, so what can be wrong with
it is mostly the same too. The first implementation's validation of that input
is a list of cases somebody already found, each with its reason. Read it before
designing the second implementation's handling, and answer each case there - by
the same check, by one the second makes differently, or by a sentence saying why
the case does not arise.

**The shape of the occasion.** A second backend was given a check on whether an
input is valid over the range a run covers. It was designed to ask the top of
the range alone, and it went through a design agent and a clean reader with
that. The adversarial tester ([[2B]]) gave it a range whose bottom lay outside
where the input is valid, and the run returned an answer. The first backend
refuses the same input where the top of the range is outside and warns where the
boundary falls inside it - the same fact about the same object. Reading that
check first would have put both ends of the range in the design.

The first implementation's checks are the population [[1F]] asks for, already
gathered and each already argued.
