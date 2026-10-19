## Traps
Only skipped/cached/ok in the first screen; 'failed' appears for the first time at line 1471.

## Reference solution
grep -n failed | head -1; grep -c.

## Why the answer is unique
integration:payments first, 3 failures. Expected answer per turn: integration:payments; 3.
