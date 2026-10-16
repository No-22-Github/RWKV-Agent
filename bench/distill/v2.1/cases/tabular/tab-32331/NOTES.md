## Traps
There is no status literally called failed.

## Reference solution
cut -d, -f3 | sort | uniq -c; count the non-success ones.

## Why the answer is unique
error+timeout+aborted.
Expected: 95; 53
