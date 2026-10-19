## Traps
The first screen shows only part of the code set; counting lines instead of distinct codes is wrong.

## Reference solution
grep -o 'code=E-[0-9]*' | sort -u | wc -l.

## Why the answer is unique
Thirteen codes are possible; the exact number is recomputed. Expected answer per turn: 13.
