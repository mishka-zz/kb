---
id: 2W
title: Build an A/B by driving both versions rather than by patching the new one to act like the old - a patched comparison compares the patch, and is blind in exactly the half the patch does not reach
kind: fact
noted: 2026-09-12
tags: method, review, testing, carried
provenance: judged: worked out on another record, where a change altered two
    things about a scan, the comparison patched one of them, read hundreds of
    thousands of samples and reported none unlike, while a break in the other
    half sat in the corpus and was found by driving the older module for real
related: 2B, 1G, 2S, 1T, 3A
---

The cheap way to check that a change moves no answer is to make the new module
behave like the old one and compare it with itself. It is cheap because nothing
has to be built: one knob, one `monkeypatch`, one sweep.

It is also blind wherever the knob does not reach, and it says nothing about
being blind. **The half of the change the patch leaves alone is identical on
both sides of the comparison**, so every answer agrees there whatever the code
does, and the sweep's size makes that look like evidence rather than like an
identity.

**The reference is the old code, run for real.** `git show <commit>:<path>`
into a file, or a worktree at the tag, loaded beside the new one and driven
against the same data. It costs a few minutes and it is the only form that can
disagree.

Two more things the same occasion taught, and both are about what a comparison
holds fixed:

* **vary the parameters a caller happens to pin.** The comparison drove the two
  settings two callers use, and the break needed a third. A free parameter of
  the function is not a property of the code;
* **vary the population's own sampling.** Where the inputs come off one
  policy's lattice, which of them land on the case that breaks is decided by
  that lattice.

[[1G]] is the rule one level up - a comparison that never leaves the pair has
measured nothing - and [[1T]] says how to prove such a digest can see at all.
