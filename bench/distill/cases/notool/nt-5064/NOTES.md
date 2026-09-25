## Traps
- TR-NOTOOLNEED: the clause file, the README and the schema note are workspace props; the expression follows from the database's own function set. The near-miss decoy `date_trunc('week', ordered_at)` truncates to a week boundary, which splits one calendar month across several buckets, so a monthly count built on it is wrong.

## Reference solution
1. Answer from PostgreSQL: `date_trunc` returns the timestamp truncated to the named unit.
2. Reply with `date_trunc('month', ordered_at)`, the second entry being the same call with the spacing written differently.

## Why the answer is unique
The question fixes the column and the bucket, and PostgreSQL has one function that truncates a timestamp to a named unit, so the expression is `date_trunc` with the unit `'month'`. A weekly or daily bucket cannot serve: the question asks that all orders of one calendar month collapse onto a single value, and only the month unit does that. `date_trunc('month'` is recorded as an accepted spelling because the remaining argument spacing does not change the expression.
