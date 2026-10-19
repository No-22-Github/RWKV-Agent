## Traps
Row count (2600) is not the distinct count; header must be excluded.

## Reference solution
wc -l, head; cut -f3 | sort -u | wc -l.

## Why the answer is unique
Recomputed from the fixture. Expected answer per turn: 420.
