---
id: 2G
title: An instruction is followed and an overview is not, so being accurate is not what earns a section its place
kind: fact
noted: 2026-08-28
tags: method, record, carried
provenance: cited: Gloaguen, Mundler, Muller, Raychev and Vechev, Evaluating AGENTS.md - Are Repository-Level Context Files Helpful for Coding Agents?, arXiv 2602.11988v2, 2026-06-23, sections 4.2 and 4.3
related: 1J, 1B, 1G
---

Measured over four agent-and-model pairs, on 300 issue-resolution tasks from
popular repositories with a generated context file and 138 from repositories
that carry a developer-written one:

- **An instruction naming a tool or a practice is followed, and by a large
  multiple.** A tool named in the file is used about 1.6 times per instance
  against under 0.01 when it is not; a repository-specific tool 2.5 times
  against under 0.05. Whatever else is at stake, it is not instruction
  following.
- **A repository overview changes nothing.** Agents did not reach the file the
  patch had to touch in fewer steps with one than without. One agent went
  looking for the context file it already held.
- Cost rose by a fifth, the mechanism being more exploration and more testing.

So the rule: **a piece of standing context earns its place by naming an action
or a refusal.** A description of structure does not change what gets done, and
calling it orientation does not make it change anything.

**Where this is not [[1J]].** 1J cuts a section that has gone stale, and its
test is whether a line would survive somebody renaming a symbol - which condemns
an inventory and acquits an accurate one. This says an accurate overview does
not pay either, because being right is not the same as changing what gets done.
The test is the one this record already applies to every other claim - would
removing it change what somebody does?

**What that study does not establish, and what it is not evidence for.**

- Its success is one issue resolved in one session, scored by generated tests
  passing. It cannot see a criterion that stops a closure, a rejected design
  that is not proposed again, or a measurement that is not re-run - which is
  most of what this record is for.
- Its headline is a null result, and a null at that size does not exclude a
  modest effect. One comparison in it is significant, and it is that
  developer-written files beat generated ones.
- Python, and repositories popular enough to be in a benchmark. The authors say
  themselves that repository specifics may already sit in the model's parametric
  knowledge and nullify the effect, and name a niche toolchain as the case still
  to do. A component answerable to observed behaviour rather than to a
  published grammar is that case: what a record holds about it was obtained by
  experiment and is not recoverable by knowing the language well.
- The cost it charges against context is more testing and more exploration. In a
  project whose subject is gates that is the wanted behaviour, and a
  pass-or-fail metric cannot tell it from waste.

Its own conclusion is that a change like this should be evaluated before it is
deployed, which applies to deploying its conclusion. So what follows from it
here is a measurement to make, not a section to cut.
