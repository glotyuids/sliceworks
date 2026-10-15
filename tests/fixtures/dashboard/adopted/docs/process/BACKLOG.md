# Product backlog

## Increment 2: gate closure (M1)

Exit demo: `scripts/dev/demo.sh 2`, the offline whole cycle with a restart. Scenarios: G-01, G-02.

| slice | state | content | depends on | writer |
|---|---|---|---|---|
| slice-01 land-inflight-set (process) | proposed | commit the in-flight set | NH-01 | slice-implementer |
| slice-02 fix-gate-failures (fix) | proposed | one fix per red package | slice-01 | slice-implementer |

## Increment 3: trace export (M1, side track)

Exit demo: `scripts/dev/demo.sh 3`, the export matches the summary. Scenarios: G-03.

| slice | state | content | depends on | writer |
|---|---|---|---|---|
| slice-03 trace-export | draft | a script over the retained runs | none | slice-implementer |
| slice-04 old-plan | cut | replaced by slice-03 | none | slice-implementer |
