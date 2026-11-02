---
id: 3G
title: No new capability lands while an entry marked able to return a wrong answer quietly is still open
kind: decision
noted: 2026-09-12
decided: 2026-09-12
tags: method, release, carried
because: A capability added on top of a layer that can return a wrong answer
    quietly multiplies the surface on which that happens, and a convention
    nothing enforces claims something nobody checks. Neither is a feature, so
    neither is ever urgent on its own - which is why they are stated as a bar on
    features rather than as work in a queue.
related: 1H, 1Q, 2Z
---

The bar has two halves, and both are answered before a new capability lands.

**The open entries tagged `quiet`.** The tag marks a fault that can hand back a
wrong answer with nothing said, and `state` prints `!` beside each one it
lists. Ask the record for them - `kb.py find --field tags=quiet` - rather than
trusting a paragraph that lists them. A list of what a query returns goes stale
on the next entry. `check` refuses the tag in a terminal place, because the
query that gathers them does not filter by place.

An entry leaves this half by closing, or by being made loud. A fault that now
says so when it happens has stopped being quiet, even where it is not yet fixed.

**A convention nothing enforces.** Where the project's instruction claims
something about the code - a style, strict typing - and no tool checks it, the
claim is a wish ([[1Q]]). The tool that would check it goes on this list. It
leaves the list when that tool runs over the whole tree on every change, with a
guard that fails if its scope narrows, because a passing run over less of the
tree says nothing about the rest ([[1H]]).

**The occasion it came from.** The list held the open faults that could return a
wrong number quietly, and a type checker. Style had already left it, the day a
linter and a formatter started running over the whole tree. The type checker
left it the same way. What it found was declarations that did not describe the
code, and nothing that returned a wrong number, which is what its entry had
predicted. The faults left the list by being made to say so when they happened,
before they were fixed.
