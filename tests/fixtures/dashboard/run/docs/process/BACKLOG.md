# Product backlog

## Increment 0: walking skeleton

Exit demo: the service starts, stores one record and returns it. Scenarios: R-001, R-002. Human acts: none.

| slice | state | content | depends on | writer |
|---|---|---|---|---|
| slice-01 service skeleton | merged | the process and its health check | none | slice-implementer |
| slice-02 record storage | merged | one table and its repository | slice-01 | slice-implementer |

## Increment 1: search and import

Exit demo: an imported file is searchable. Scenarios: R-003 to R-006. Human acts: NH-01.

| slice | state | content | depends on | writer |
|---|---|---|---|---|
| slice-03 search endpoint | active | full-text search over records | none | slice-implementer |
| slice-04 import job | review | CSV import in the background | none | slice-implementer |
| slice-05 ranking ∥ | ready | relevance ranking | slice-03 | slice-implementer |
| slice-06 export | draft | export of a result set | none | slice-implementer |

## Increment 2: sharing

Exit demo: a second user opens a shared result. Scenarios: R-007. Human acts: none.

Proposed slices: share links (signed, expiring); access checks; audit log.
