---
id: 1C
title: Run mutations with `PYTHONDONTWRITEBYTECODE=1` - CPython validates a cached `.pyc` on the source's mtime and size, so a same-size mutation reverted inside a second leaves the cache holding the mutant
kind: fact
noted: 2026-09-12
tags: testing, python, method, carried
provenance: judged: worked out on another record, by an any-to-all swap written
    and reverted inside one second, which survived its own restore and failed a
    test twenty minutes later with correct source on disk
related: 1E, 2Q, 3A
---

`any` for `all`, `>` for `<`, a digit for a digit - the byte count does not
move, and neither does the second on the clock. CPython then trusts the cached
bytecode, and the mutation survives its own restore to fail a test later, with
correct source on disk.

**So mutation testing runs with `PYTHONDONTWRITEBYTECODE=1`**, wherever [[1E]]
is applied.

It is the false **survived** that costs you: that reads as a missing test, and
the fix for a missing test is to write one that cannot fail. If a result ever
looks impossible, clear the `__pycache__` directories before believing it.
[[2Q]] is the other way a mutant outlives its run.
