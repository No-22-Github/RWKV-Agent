## Traps
Three subfolders and 330 names; filenames, not modification times, carry the date. 08-20 itself counts.

## Reference solution
find | sed extract date | awk compare | wc -l.

## Why the answer is unique
Recomputed from the file names. Expected answer per turn: 129.
