## Traps
Empty files are scattered; a directory listing is long and cut off by its default limit.

## Reference solution
find -size 0 | wc -l.

## Why the answer is unique
Recomputed from the fixture. Expected answer per turn: 29; 4.
