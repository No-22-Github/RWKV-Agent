## Traps
Three near-equal 404 paths; first screen has no 404 at all.

## Reference solution
grep 404 | awk '{print $7}' | sort | uniq -c | sort -rn.

## Why the answer is unique
/api/v1/export leads clearly. Expected answer per turn: /api/v1/export; 113.
