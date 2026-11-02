---
id: 2C
title: Ask the platform before building against it, and before calling a defect ours
kind: fact
noted: 2026-08-31
tags: method, carried
provenance: judged: worked out on another record, where the owner's question
    "what about the platform's own?" was right every time it was asked, and where
    defects blamed on our code repeatedly reproduced on a bare platform
related: 1B, 1Y, 1J
---

Ask the platform rather than your memory, and answer by running it rather than
by reasoning about it.

**Before building a component**, look for what the platform already provides,
and find out what it will not do before designing around an assumption. The
shape of the failure is a decision taken on a remembered capability: a
normalization the standard library does not perform, a regular-expression
feature the engine does not have, a numeric mode the runtime quantizes
differently than expected. Each is one command away from being a fact and one
assumption away from being a rewrite.

**Before fixing a reported defect**, build the smallest case that uses only the
platform and see whether it fails there too. The answer changes what to do, not
merely what to say: a fault that reproduces on the bare platform is not ours to
fix in our own code, and compensating for it at runtime is its own kind of
damage - a correction applied on every pass overrides whatever else touched the
same thing, including a deliberate choice made upstream.

**The normative documents are a platform too.** A standard settles what a
well-formed input is, and reading the text is cheaper than reasoning from a
recollection of it. Where it is silent - and on adversarial input a standard
mostly is - that silence is itself the answer, and the rule then belongs to
observed behaviour, said so explicitly.
