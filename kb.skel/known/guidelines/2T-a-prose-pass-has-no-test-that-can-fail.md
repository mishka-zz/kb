---
id: 2T
title: A prose pass that only shortens comments has no test that can fail, so a clean reader is the whole instrument
kind: fact
noted: 2026-09-12
tags: method, review, prose, conventions, carried
provenance: judged: worked out on another record, where five days of comment
    prose was cut out of a codebase by agents working file by file, the suite
    was green throughout, and two clean reviewers over the diff found a claim
    inverted in each half of it
related: 2D, 2B, 1P, 1B, 1J, 2Z
---

Every other change answers to something that runs. A pass that edits only
comments, docstrings and specification prose is not: the code is identical by
construction, so the compiler, the linter and every tier of the suite pass
exactly as they did before, and they would pass just as well over prose that now
says the opposite of what the code does.

## What goes wrong, and it is one thing

**Shortening inverts claims.** Not "loses detail" - inverts. A sentence carrying
a dependence and its exception is shortened to the exception, and now denies
the dependence. A qualifier that made an example real is dropped, and the
example is a case the code never reaches. A reason and a caveat are welded by a
colon, and the caveat is left unnamed. Each of these reads well. None survives
being held against the code beside it.

Two reviewers, one per half of the same diff and neither knowing what the other
had, each reported this fault first, and each found it in prose that had been
shortened rather than deleted. Deletion is safe; compression is where the
meaning goes.

## So the instrument is a reader, and it is the only one

- **Delete in preference to shortening.** A comment the code already makes is
  the cheapest thing in the diff to get right.
- **A clean reader afterwards, never the author.** The author remembers what the
  sentence meant and reads it back in. [[2B]] is the same rule for changes that
  do run.
- **Brief the reader on the fault.** "Find a claim that changed meaning" finds
  them; "review this diff" finds bold and dashes.
- **Every claim is held against the code beside it, not against the text that
  was cut.** That is also how a sentence stale long before the pass touched it
  gets found ([[1P]]).

A reviewer's finding is a hypothesis here as anywhere ([[1B]]), and it costs a
read of the function under the sentence.
