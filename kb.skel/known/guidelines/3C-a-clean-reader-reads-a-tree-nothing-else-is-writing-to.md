---
id: 3C
title: Launch a clean reader against a tree nothing else is writing to - it reads the files as they are, so a mutation run in flight comes back as a defect argued as well as any real one
kind: fact
noted: 2026-09-12
tags: method, review, testing, tooling, carried
provenance: judged: worked out on another record, where a mutation sweep held a
    mutant on disk for a quarter of an hour while a clean reader read the same
    working tree, and the reader's first and longest finding was the mutant, with
    three true consequences derived from it
related: 2B, 2Q, 1C, 1B, 1K
---

[[2B]] puts a clean reader on the change and says what it is for. It says
nothing about the tree the reader looks at, and there is nothing to say it: the
reader opens files, and a file says what it says at the moment it is opened.

A mutation run holds a mutant on disk for as long as the tier takes, and a
reader launched beside it reads the mutated line as the change under review.

**What comes back is not noise.** A finding built on a mutant is coherent,
specific and well argued, because the mutant is a real edit - an import that
lost its only user, a docstring that no longer describes the loop, a constant's
comment naming a call the loop no longer makes, every one of them following and
every one about code nobody wrote. What it is not is a finding about the
change.

**[[1B]] is what makes it expensive.** A reviewer's finding is a hypothesis and
is checked before it is believed, so the cost is not the wrong fix - it is the
checking, paid on the whole cluster rather than on the one line. The cheaper
failure is the one to fear: taking the reading at face value and reverting a
change that was never made.

**The guard is scheduling, and it is free.** A reader goes out against a tree
nothing else is writing to. Where a long run has to overlap, the reader is told
what is in flight and which files it touches, so that a finding there is a
question rather than a report. Better still, the reader is told a commit to
read - it can take its own copy with `git show` and work against a state that
has a name, which survives an edit nobody warned about.

**And the settlement is one command.** `git diff --stat` over the source
answers it, and the reader withdraws the finding on being told. That is the same
question [[2Q]] asks after a mutation run for a different reason. Both are one
habit: before believing anything a reading said, ask git what was on disk while
it was reading.

[[1K]] is the rule one level up, and this is its shape for a reading rather than
for a measurement: an edit made in the middle of a reading is reported as the
thing being read.
