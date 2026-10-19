## Traps
The overall largest file lives under vendor/cache and must be excluded.

## Reference solution
find with -not -path | sort -rn | head.

## Why the answer is unique
run_peak.log is the largest outside vendor. Expected answer per turn: run_peak.log; 3932.
