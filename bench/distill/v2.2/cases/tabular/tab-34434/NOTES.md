## Traps
The number of extra rows and the number of repeated ids coincide only if nobody appears three times; counting lines is not the same as counting ids.

## Reference solution
cut -f1 | sort | uniq -d | wc -l.

## Why the answer is unique
Recomputed from the fixture. Expected answer per turn: 37.
