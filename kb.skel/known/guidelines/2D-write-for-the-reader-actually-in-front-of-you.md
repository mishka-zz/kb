---
id: 2D
title: Write for the reader actually in front of you, in code and in a report alike
kind: fact
noted: 2026-08-28
tags: method, conventions, prose, conversation, carried
provenance: judged: the reader of this code came to it to change it and brought the domain with them, and the reader of a report is not holding the record its identifiers point into
related: 1Z, 2E, 1J
---

Two readers, opposite in what they arrive with, and the same rule about which of
it to spend.

**A comment's reader knows the domain.** They brought it, and restating it costs
them the attention the next line needed. What earns a comment is what **this
project chose**, and why the obvious alternative was not: a magic number is
named and justified where it stands, and a standard one is written and left
alone. What is written as the justification is answerable to something, which is
where this can go wrong even when the number is right ([[1Z]]).

**A report's reader is not holding the record.** An entry identifier, a task
number, a milestone name and a bare file path are handles into something they
cannot see; each is expanded into what it says, or left out. And say **how much**
actually changed - "the gate moved" and "the gate moved by a tenth of its
tolerance" are different reports, and only the second lets them decide anything.

Prose written for the repository is not prose written for a conversation, and
the conventions are not the same one.
