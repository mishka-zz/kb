---
id: 3M
title: A check the test doubles cannot make is a runnable script with its own command line, not a test
kind: fact
noted: 2026-09-12
tags: method, testing, carried
provenance: judged: worked out on another record, where checks had to be
    written as scripts because the suite's stubs for the platform the code runs
    inside and the libraries it calls answer every question the way they were
    told to
related: 1Q, 1E, 3N
---

A fast suite that runs against stubs gets from each stub the answer it was told
to give. That makes a whole class of check **invisible under the test runner by
construction**, not merely untested:

- a corruption that only a real write and read back produces, because the stub
  stores whatever it is handed and gives it back;
- what a real interface component returns, and what it does with the text it
  is handed;
- anything where a stub's summary of an object stands in for the object - an
  outline answering for something that does not fill it;
- what a module does when the real platform loads it, against a real version
  and a real environment, rather than against globals the suite injects itself.

None of those becomes a test by being written harder. Each becomes a script:
runnable by somebody who was not there, carrying **its own command line and its
own interpreter in its own docstring**, because the interpreter is half the
point and is the half a reader will get wrong.

The script is a *pair* to a test where one exists, covering the half the suite
cannot run - not a substitute for writing the test. And a script whose only
reader is its author is one nobody re-runs, so the command line goes in the file
and never in a session's notes.

## A guard makes its own failure case unreproducible

A script that refuses a bad input cannot produce that input's evidence. On the
occasion it came from, the input an external program aborted on was built by hand,
past a guard the archived script had no way to lift, and the result then sat in
the archive beside scripts that could not rebuild it. A clean reader found it;
nothing in the directory could have.

So a script that refuses gets a way to be told to go on anyway, in its own
command line beside the rest. The switch is not a convenience. A guard creates a
case that only the switch can produce, and that case is exactly the evidence the
guard exists because of.
