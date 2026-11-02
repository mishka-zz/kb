---
id: 3R
title: A cost entry closes by taking work away, and making the same work cheaper per unit is the change that can come back dearer
kind: fact
noted: 2026-09-12
tags: performance, method, carried
provenance: judged: worked out on another record, reading across the cost
    entries closed on one hot layer, where every win was a removal and each
    attempt to make an operation cheaper while keeping it measured dearer
related: 3P, 1Y
---

Read across what closed on the occasion it came from, every win was a removal:

* a numerical integral replaced with the closed form of the same integral;
* a loop taken from running to its budget down to a single pass ([[3P]]);
* a scan moved to where the data already sat;
* a search stopped from asking further than an answer can bind;
* a walk taken through an existing index instead of gathering its own;
* one lattice laid where two were laid over the same data.

Each of those deletes an operation rather than shortening it. Nothing closed by
making an operation cheaper while keeping it.

**And the attempts at the second came back dearer.** The clean case was measured
both ways: a search sent only as far as the answer could bind is a shorter
search, and it costs more, because a search that finds nothing within its bound
falls back to looking through everything. Shortening the question raised the
odds of the expensive answer.

## What to do with it

Ask what the operation is *for* before asking what it costs. Where the answer is
"nothing that binds", the operation goes. Where the answer is "this, and the
caller needs it", the constant in front of it is rarely where the entry is.

A unit made cheaper is also the change whose cost is hardest to predict, because
what it saves is local and what it costs may not be. A removal cannot have that
fault: the work is not done, so nothing downstream of it fires.
