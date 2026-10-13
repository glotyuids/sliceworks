# Refocus <D-id> · <title of the pivot>

<!-- sliceworks 0.6.0. The refocus audit (method chapter 14): every document, scenario, row, contract, spec and threat model read against the pivot decision by the two read-only analysts; the coordinator applies the verdicts and records what it did. One file per pivot, under <state-dir>/refocus/. The owner reads this file and nothing else. -->

Pivot: D-<n> · <date> · evidence: <round, metric, incident or owner statement>
Promise before: <one line> → after: <one line>

## Verdicts
| item | kind (document, scenario, row, contract, spec, threat model) | verdict (keep, amend, archive) | reason | applied (date and the archive path, or the D that amended it, or "reviewed") |
|---|---|---|---|---|

## Dropped, added, moved
- Dropped: <scenario and row ids; each keeps its id and references D-<n>>
- Added: <scenarios and rows, with their checks>
- Moved: <ids and their new milestone or increment>

## Archived
| file | archived as | replaced by |
|---|---|---|

## Owner summary
<five lines at most: what changed, what was archived, what the owner may veto and by when>
