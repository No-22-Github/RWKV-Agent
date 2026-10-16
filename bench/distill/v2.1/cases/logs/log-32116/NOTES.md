## Traps
- TR-DEFN: the window edges (inclusive/exclusive) are spelled out and lines sit exactly on them (and 1 ms / 1 s inside the upper edge).
- TR-DECOY: the status code also appears inside durations/bytes/paths; the file also holds the previous evening, so a time-of-day filter without the date over-counts.

## Reference solution
Filter the day, the exact status field, then awk string-compare the time-of-day against the window edges.

Expected tokens per turn: 24 13:00

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
