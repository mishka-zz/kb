---
id: 1Q
title: A suite that passes says nothing about the environment it declares, unless something compares the two
kind: fact
noted: 2026-08-31
tags: method, testing, packaging, carried
provenance: judged: worked out on another record, where a transitively-installed
    dependency kept a suite green while the declaration never named it, and where
    declaring a language floor immediately turned up code written for an older
    one
related: 1S, 1A, 1W
---

A dependency arrives transitively, the suite goes green, and the declaration
never mentions it. **Nothing in a passing run distinguishes *installed* from
*declared***, so the environment the tests actually ran in is one no document
describes, and the first person to install from the declaration is the one who
finds out.

The check is to compare the two artefacts directly - what the project declares
against what the environment provides - and it is cheap, because neither side is
a measurement.

**Declaring a floor is the same check from the other end.** A minimum version
named and then actually run against turns up code written for an older or newer
one, in places nothing else looks. A declaration nothing compares against is a
wish; a declaration something compares against is a test that costs nothing.

**The two places it hides.** A language floor a module declares while the
build uses a newer toolchain: a green run says the code works on the toolchain
in use and nothing about the floor claimed. And a requirements file with nothing
comparing it against what a working environment actually has. The record
already treats the toolchain as load-bearing - `stale` refuses by name rather
than falling back, because a test run under a different toolchain answers a
question the record did not ask - which is the same concern one step earlier.
