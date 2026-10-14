## Traps
- TR-NOTOOLNEED: the clause file and the review note are workspace props; the clause follows from SQL semantics. The near-miss decoy `WHERE COUNT(*) > 10` is the shape a model reaches for when it forgets that a filter over an aggregate is not a row filter: every engine that offers the grouping clause rejects an aggregate in WHERE.

## Reference solution
1. Answer from SQL: a condition on the number of rows in a group belongs to the clause evaluated after grouping.
2. Reply with `HAVING COUNT(*) > 10`, with `count(*)` and `>= 11` accepted since the count is an integer.

## Why the answer is unique
The question asks for a restriction on groups, and SQL evaluates group conditions in one clause only, `HAVING`; `COUNT(*)` counts the rows of the group and "ten or lower is discarded" is the strict comparison against 10. `WHERE COUNT(*) > 10` is not a second reading but an illegal statement, since the engine evaluates WHERE per row before any group exists. `HAVING COUNT(*) >= 11` says the same thing because the count cannot be fractional, so it is accepted as the same answer written differently.
