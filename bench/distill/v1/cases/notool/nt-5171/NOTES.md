## Traps
- TR-NOTOOLNEED: sql/lock-clauses.tsv and README.md are props. Locking behaviour is a property of the database, so no file has to be read. The near-miss decoy `FOR UPDATE SKIP LOCKED` takes the same exclusive lock but refuses to make anyone wait: it leaves the locked rows out of the clerk's statement instead, so the ledger's own read silently loses rows.

## Reference solution
1. Answer from the database: the clause that locks the rows a statement reads until the end of the transaction is `FOR UPDATE`.
2. Reply with `FOR UPDATE`, or the same clause with the table named, `FOR UPDATE OF hide_batch`.

## Why the answer is unique
The question asks for the clause that makes the clerk wait, and `FOR UPDATE` is the clause that takes the exclusive row lock and holds it to the end of the transaction, which is what blocks the clerk. `FOR UPDATE SKIP LOCKED` is not a second reading: it is the same lock with the opposite answer to a blocked reader, since the clerk would skip the ledger's rows rather than wait, and the question asks for a wait. Naming the table narrows the same clause and is accepted.
