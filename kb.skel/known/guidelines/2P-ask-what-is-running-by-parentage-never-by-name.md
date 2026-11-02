---
id: 2P
title: Ask what is running by parentage, never by name - a filter for what you expect to be there cannot see what leaked
kind: fact
noted: 2026-08-31
tags: method, agents, review, harness, carried
provenance: judged: learned in a sibling session on this same harness, where three
    claims of "nothing of ours is running" rested on patterns invented to match
    the work that had been launched, while two processes left behind ran on for
    fifty minutes
related: 2B, 1B, 2R
---

Asking `ps | grep <the names you launched>` answers whether the things you
thought of are running. It cannot answer whether anything is, and **the two read
identically when the answer is empty.** What leaked in the occasion above
matched none of the patterns - a wait loop polling for output whose producer had
already been killed.

**Ask by parentage.** `pgrep -P <the session's pid>` is a closed set: whatever
this session started is in it, whatever it is called. Read it whole, and read
the command of anything unfamiliar rather than filtering it out.

**A completed agent is not a quiet one.** A subagent's shell commands run as
children of the *parent session*, not of the agent, so an agent reported as
`completed` can have live processes still burning a core - and each time one
exits, the agent is woken to report again, which is why one of them filed the
same findings three times with each firing looking like new work. This is
harness behaviour rather than any codebase's, so it holds here unchanged.

**The failing move generalises past processes.** A long list of things ruled out
is not progress when every one of them asked the same kind of question, and a
filter built from your own expectations is exactly that question, asked once.
