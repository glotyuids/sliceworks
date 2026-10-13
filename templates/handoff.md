---
allocation: alloc-<slice>-r<n>
result: CANDIDATE | BLOCKED | HOLD
head: <full 40-character commit>
base: <full 40-character commit the work was built on>
verification: {tier: t1, log: <path>, result: pass | fail | NOT_RUN}
proof_state: compiled | executed | runtime-verified
written: <timestamp>
---

# Handoff <allocation>

<!-- sliceworks 0.5.0. Committed by the worker on its branch before it returns (method chapter 19). The CANDIDATE, BLOCKED or HOLD message is a pointer to this file; this file is the record. -->

## Completed scope
<rows flipped, files changed in one line each>

## Verification
<what ran, from which commit, with which boundary (compile-only, executed, runtime); the RESULT line; what was NOT_RUN and why>

## Findings decided out of scope
<id: reason>

## Blockers
<what stops the next step; the default the worker would apply>

## Next bounded action believed authorized
<one sentence, or "none">

## Stop gate output
<what the T0 gate printed on the last turn, verbatim first line>
