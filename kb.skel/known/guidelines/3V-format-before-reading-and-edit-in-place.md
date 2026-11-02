---
id: 3V
title: Format before reading and edit in place - a file an agent's session has read comes back into its context whole each time something else rewrites it
kind: fact
noted: 2026-09-13
tags: method, agents, carried
provenance: measured: on another record, over a session that ended with three
    quarters of its context spent on notices that a file it had read had changed
    on disk, each carrying the file, after a formatter, mutation runs and
    scripts rewrote the same few modules again and again
related: 2B, 2R, 3D, 3C
---

An agent harness tracks the files a session has opened with its reading tool.
When one of them changes on disk by any route other than the session's own edit
- a formatter, a script that rewrites it, a mutation run putting it back - the
next turn carries a notice that it changed, and the notice holds the file, or as
much of it as fits. Nothing asked for it and nothing in the turn needs it.

So:

- **Run the formatter before reading a file, not after.** A file formatted once
  and then read is not echoed again by the next format, which changes nothing.
- **Change a file the session has read with the edit tool.** An edit made that
  way is the session's own and comes back as a line, where a script rewriting
  the same file comes back as the file. A mechanical change - a renamed key, one
  token in several places, a class replaced whole - is exactly the case the edit
  tool handles best, and a splice also skips its check that the text replaced is
  the text read.
- **Look at a file with `grep` or `sed -n`, not the reading tool, where something
  other than the edit tool is going to change it.** A slice printed through the
  shell is not tracked, so it is not echoed when a script, a formatter or an
  agent's mutation run rewrites the file later.
- **Put a run that rewrites and restores files, or solves a population and
  tabulates it, in an agent that returns the summary.** A mutation harness
  restores every file it touched, and each restore is a change on disk.
- **Compact at the boundary between stages of the loop** ([[2B]]), where what the
  next stage needs is already written into the entry. [[2R]] is why it has to be
  written down first.

On the record it came from the rule was broken on piece of work after piece of work,
each time the same way: a change that looked too small or too repetitive for the
edit tool reached for sed or a splice.
