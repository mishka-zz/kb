---
id: 2S
title: A check built on a reduction is blind to whatever the reduction leaves out - a summary cannot say two things are the same, and a deduplicated record cannot say a contribution went missing
kind: fact
noted: 2026-08-31
tags: method, testing, record, carried
provenance: judged: worked out on another record, where a guard comparing two
    objects by their total size passed one placed slightly off centre, and
    where a deduplicated diagnostic dump silently dropped the one request a
    rule was about
related: 1E, 1S, 1G, 1K
---

A reduction is any single number or normalized record standing in for the thing
itself: a volume, a count, a mean, a hash of a subset, a deduplicated list. Each
is a sound thing to assert **about** a subject. None of them is a way to ask
whether two subjects are the same, because each has a null space - a family of
differences it maps to one value - and a check written on it reads green over
that whole family.

**The question to ask of a comparand is: which changes leave this number
alone?** It is answerable before the check is written, rather than after an
adversarial tester has found the case.

**And the wider form, which is the one that bites hardest.** The reduction may
not be in the comparand at all but in *what the test can see*. Where the record
a test reads has already merged or deduplicated its entries, the assertions can
be perfectly written and still have nothing to fail on: the distinction was
thrown away upstream. So the question widens - not only *which changes leave
this number alone*, but *which changes leave the record alone* - and it is asked
of the artifact before the assertions are written.

**It is not an argument for asserting everything.** A summary is the right
comparand where the claim is about the summary. What this rules out is the
substitution: a claim about identity answered by a claim about size, which reads
the same on the way in and checks a fraction of it.
