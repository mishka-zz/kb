---
id: 1D
title: Pass `abs=0.0` below about 1e-10 - `pytest.approx` keeps an absolute tolerance of 1e-12 even where only `rel=` is given
kind: fact
noted: 2026-09-12
tags: testing, python, method, carried
provenance: source: pytest's own `python_api.py`, where DEFAULT_ABSOLUTE_TOLERANCE
    is 1e-12 and the comparison is max(rel * expected, abs)
related: 1E, 1A
---

The comparison is `max(rel * expected, abs)`, and `abs` defaults to 1e-12
whether or not `rel` was given. Anything small enough to sit under that floor
- a probability in the tail of a calibrated score, a per-token weight, a ratio
of two counts over a large corpus - passes `approx` whatever its relative error,
or must pass `abs=0.0` explicitly, or be compared as a dimensionless ratio
against 1.0 instead.

On the record it came from it silently passed a quantity off by a factor of two and a
rounding mode that was absolute where it should have been relative. [[1E]] asks
for tolerances rather than snapshots; this is the one place a tolerance is
looser than it reads.
