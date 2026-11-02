---
id: 3A
title: Install a probe where its caller resolves the name - replacing the attribute in the defining module stops intercepting the moment a caller imports the function by name
kind: fact
noted: 2026-09-12
tags: method, testing, python, carried
provenance: judged: worked out on another record, where a probe that had been
    patching the one module both the definition and the call were in recorded
    half the count after a split moved the definition out, and the digest on the
    old tree came back byte for byte after the fix
related: 1T, 2S, 2W, 2B, 1C
---

An instrument that wraps a function replaces the attribute on a module. Which
module is the question. `from .field import settle` binds `settle` into the
caller's own globals at import time, and the caller resolves it there for the
rest of the run. Replacing `field.settle` afterwards rebinds a name nobody
reads.

Nothing complains. The probe still runs, the wrapper is still installed, and
the records that arrive are the ones from callers that happened to reach the
function through its own module. The count comes back lower, and a count is not
something an instrument is usually read for.

**Wrap every binding, not the definition.** Walk the package, and set the
attribute on each module holding the same object under that name:

```python
for module in modules:
    if getattr(module, name, None) is original:
        setattr(module, name, wrapped)
```

**The occasion is a split.** Before it, the definition and both callers sat in
one module, so patching the definition was patching the binding and the probe
was complete. The split moved the definition and left the callers holding their
own name - which is the form `from ... import name` produces everywhere. So an
instrument written against a tree before a split is worth re-checking against
the tree after it, and the check is cheap: run the probe on the old tree, and
demand it reproduce the digest it produced there. [[1T]] is the rule: a sweep
that finds nothing is a claim about the instrument first.
