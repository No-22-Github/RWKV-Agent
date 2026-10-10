## Traps
- TR-NOTOOLNEED: sql/insert-clauses.tsv, README.md and notes/load-notes.txt are props. Collision handling is a property of the database, so nothing on disk has to be read. The near-miss decoy `ON CONFLICT (kiln_id) DO NOTHING` avoids the error but leaves the stored row untouched, so the values from the repeated firing are dropped.

## Reference solution
1. Answer from PostgreSQL: the clause that follows the values list of an INSERT and handles a collision on a named key is `ON CONFLICT (<key>)`, and the action that rewrites the stored row is `DO UPDATE`.
2. Reply with `ON CONFLICT (kiln_id) DO UPDATE`.

## Why the answer is unique
The question asks for the clause under which the values just supplied end up in the table, and `DO UPDATE` is the conflict action that rewrites the stored row from the values of the attempted insert. `DO NOTHING` cannot be a reading of the question: it is the conflict action that discards the attempted insert, so the stale row the question describes stays in the table.
