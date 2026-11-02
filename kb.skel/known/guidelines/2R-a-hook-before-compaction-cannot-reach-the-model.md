---
id: 2R
title: A hook that fires before a compaction cannot reach the model, so nothing that is only in working memory survives it unless a turn writes it down
kind: fact
noted: 2026-08-31
tags: method, harness, hooks, carried
provenance: measured: 2026-08-30, in another record, by a hook on the harness's
    event before compaction emitting a marker string appearing nowhere else in
    the tree, and looking for it after the compaction
related: 1N, 2M
---

The hook fires, and it is told which session, which transcript and what
triggered the compaction. What it prints is not put before the model: the event
takes no context for the model, and what it can do is show a message to the
person or stop the compaction. No turn is given between the hook and the
compaction.

**So a compaction cannot be prepared for automatically.** A hook is a shell
command: it can read the disk and it cannot read a session. Anything that is
only in working memory - a measurement not yet written down, a decision taken
and not recorded, a route ruled out - is lost unless a turn spends itself
writing it. That is the argument for catching a thing when it is found rather
than at the end of the session.

An event after compaction can reach the model, where the harness has one.
Nothing needs arming on it: what a compaction takes is the standing context,
and an instruction to run `kb rules` and `kb` again brings that back.

Carried: it was measured on one agent harness. Ask the harness in use which of
its events can put text before the model, and rewrite this on that answer.
