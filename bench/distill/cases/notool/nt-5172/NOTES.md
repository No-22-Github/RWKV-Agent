## Traps
- TR-NOTOOLNEED: sql/window-clauses.tsv and README.md are props. Window function behaviour is a property of SQL, so nothing has to be read. The near-miss decoy `RANK() OVER (...)` gives tied rows the same position and then skips positions, so two readings that share a timestamp are both numbered 1 and the group no longer has one row in the first position.

## Reference solution
1. Answer from SQL: numbering the rows of a group without gaps is `ROW_NUMBER()`, and the group and its order are given by the window's `PARTITION BY` and `ORDER BY`.
2. Reply with `ROW_NUMBER() OVER (PARTITION BY instrument_id ORDER BY reading_at DESC)`.

## Why the answer is unique
The question asks for one row per group numbered 1 and it names the ordering key, and `ROW_NUMBER()` is the window function that hands out consecutive numbers, most recent first under `ORDER BY reading_at DESC`. `RANK()` cannot be a reading of the question: it is the function that gives equal keys equal positions, so with a repeated `reading_at` more than one row in the group is numbered 1, which the question excludes.
