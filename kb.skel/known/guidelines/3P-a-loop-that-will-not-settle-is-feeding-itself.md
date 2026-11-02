---
id: 3P
title: A loop that will not settle is usually judged against a quantity its own output sets, and the cheapest question is which demand won
kind: fact
noted: 2026-09-12
tags: method, performance, carried
provenance: judged: worked out on another record, where an iteration ran to
    its budget on a large input, and one call asking which demand had set the
    quantity it iterated explained what a table of its passes and a profile had
    not
related: 3K, 1F, 1S, 3R
---

An iteration that neither settles nor cycles is not usually a slow one. It is
usually one whose output is fed back into whatever decides its next output, so
nothing outside it holds it anywhere.

**The shape of the occasion.** A layout loop asked a sizing component for a
spacing at an edge, laid out the rest against what that request had just set,
read back the spacing the layout produced, and offered that spacing as the next
request. The realised spacing comes out coarser than the request by a fixed
factor, because the sizing component spreads a demand made at one place over
its neighbourhood. So the request grew by that factor on every pass and stopped
only when the budget ran out.

**Ask what set the quantity before counting the passes.** The sizing component
could be asked which of its demands won - one call, one line of output - and the answer
was the loop's own demand on every pass. That is the whole diagnosis. What was
done first instead was a table of the request over the passes, then a profile
of where a pass spends its time, then a repair aimed at the growth: half a
session establishing that the sequence climbs, which the one call would have
explained.

**The tell is a loop most of whose population settles at once.** Where an input
settles immediately, the quantity was pinned by something outside the loop;
where it never settles, it was not. The split is the evidence, and it is in the
population the loop already runs over.

**The stopping test is the second half of the same lesson.** The loop compared a
request with the spacing a layout realised, and a layout fits a whole number of
spacings into a span, so the two could be equal only by luck. A stopping test has
to compare two quantities that can be equal, or it is a budget with a comparison
written on it.
