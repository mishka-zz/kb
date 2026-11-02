---
id: 3H
title: Check an entry, and a guard, against the routes that actually run
kind: fact
noted: 2026-09-12
tags: method, review, carried
provenance: judged: worked out on another record, where entries of one open
    list named a fault already fixed, put a guard on a route the user's own
    action never takes, and chose an instrument reachable on no route that
    matters
related: 1B, 1Y, 1P
---

**An entry nobody re-read is not a finding.** On the occasion it came from an entry
named a fault whose guard had already shipped. It was transcribed from a review
drafted before those commits and never re-read against the tree.

**A guard only one route passes through is not a guard.** A second entry was
real, and its guard as first written landed in a validation pass that the
user's own action never reaches. It would have missed the one route on which
all of its faults were measured. A third argued that a property needed no check
because an earlier stage guarantees it. That is true on the route that runs the
stage, and false on the route that takes a prepared input handed in from
outside.

**The instrument has a route too.** A fourth entry named the right fault and the
wrong instrument. The instrument was a diagnostic somebody else's program
prints, and it was reachable on no route that matters and unreadable where it
was.

So list the routes into the code before trusting an entry or placing a guard:
the interactive action, the batch entry point handed a prepared input, the
library called directly. Put the guard where they meet. Where they meet only at
the last step, the last step re-runs the check, even though every caller has
already run it.
