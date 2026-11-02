---
id: 3N
title: A guard that guards nothing is worse than an honest import, because it reads as handled
kind: fact
noted: 2026-09-12
tags: method, imports, carried
provenance: judged: worked out on another record, from an optional-import
    guard whose flag was assigned in both branches and read nowhere, above a
    class that used the import unguarded so the module raised regardless
related: 3M, 3H
---

A module carried a flag saying whether an optional library was importable. The
flag was assigned in both branches and read by nothing, while the class below it
used the library unguarded - so the module raised whether or not the guard
fired. A second guard in the same file was used unguarded in several methods.

Both became plain imports. That module was code that only ever runs with the
library present, and it had no reduced behaviour to offer, so there was never
anything for a guard to do.

The cost is not the dead code. It is that a reader seeing `try: import`
concludes the case is handled and stops looking, and a maintainer deleting the
flag has to prove a negative first. Where there is a reduced behaviour, guard
the import and provide the behaviour. Where there is not, import plainly and let
the failure say what is missing.

A test suite that stubs the library does not settle which side of the guard it
runs, and [[3M]] says why.
