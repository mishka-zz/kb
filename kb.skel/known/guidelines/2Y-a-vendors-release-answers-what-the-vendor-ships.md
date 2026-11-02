---
id: 2Y
title: A vendor's own release answers what the vendor ships, and a claim about a version out in the world is answered by the channels people install from
kind: fact
noted: 2026-09-12
tags: method, packaging, carried
provenance: judged: worked out on another record, where the upstream build
    system and then the upstream release page each gave a true answer to a
    question that was not the one asked, and the package channels gave the answer
    that was - one counterexample settling a universal claim that had already
    gone into a shipped file
related: 2C, 1B, 1R
---

[[2C]] says to ask the platform. This is which question the platform can
answer.

A project's build system states what its source will compile against. Its
release page states what that project itself built and published. Neither
states what a user has, because most users install from somewhere else - a
distribution, a package channel, a bundle - and every packager rebuilds the
source under its own constraints.

So a claim of the form *every version X out there has property P* is answered
by the channels, and by nothing upstream. Ask the package indexes: they are
cheap, they are current, and one counterexample settles it.

**Both wrong answers looked exactly like a citation.** The build system said
what it accepts, which reads as *no* and is a statement about compiling. The
release page said what the vendor's own binaries carry, which reads as *yes* and
is a statement about five files. The channels said a packager had built the same
release against something else, and both readings were wrong. Each was acted on
before the next arrived.

**The tell is the quantifier.** A sentence with *every* or *any* in it is about
a population, and the first question is which population the evidence in hand
describes. Where the evidence is upstream's own artefacts and the claim is about
what somebody runs, those are two populations and the answer is not in hand.

This is [[1B]] one level out: a finding is a hypothesis, and so is the evidence
behind it, which can be real, checked, and about something else.
