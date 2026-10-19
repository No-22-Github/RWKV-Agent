## Traps
Names differ and copies sit in different folders; only content hashes show the duplicates.

## Reference solution
find -exec md5sum | awk hash | sort -u | wc -l.

## Why the answer is unique
Number of distinct contents, recomputed. Expected answer per turn: 286.
