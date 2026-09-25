## Traps
- None. No trap tag is set: the verdict carries one line per check and the outcome word is the
  middle field of the line.

## Reference solution
1. Read runs/last.txt, the verdict the check run wrote (call 1).
2. Count the lines whose outcome reads passed: spoke_gauge, hub_bore and tyre_shrink (call 2).

## Why the answer is unique
Three of the five verdict lines carry passed; felly_ring and tenon_fit carry skipped, and a
skipped check was not run at all. Counting every line gives 5 and counting the skipped ones
gives 2. The answer is 3.
