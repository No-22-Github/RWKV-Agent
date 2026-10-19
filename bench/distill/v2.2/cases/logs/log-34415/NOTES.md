## Traps
Counting 'exit=' lines or all failures mixes jobs; rotate has more failures than backup.

## Reference solution
grep job | grep -vc exit=0.

## Why the answer is unique
Recomputed from fixture. Expected answer per turn: 17; 25.
