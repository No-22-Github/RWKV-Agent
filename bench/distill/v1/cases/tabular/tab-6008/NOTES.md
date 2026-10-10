## Traps
- TR-DUPROW: firings AC-330, AC-334 and AC-341 are printed two or three times each with identical
  details. Summing every line counts those firings twice and gives 281.0 instead of 247.0.

## Reference solution
1. List the workspace: the July firing log and a readme.
2. Read README.md: re-registered batches are printed again with identical details.
3. Read kilns/firings_2026-07.csv, collapse the re-printed rows to one firing each, and total the
   hours: 247.0.

## Why the answer is unique
The readme says a re-printed row is the same firing, and each repeated block matches on every
column including firing_id, so the repeated lines are the same event rather than extra firings.
Counting them twice is the decoy 281.0; the kiln cannot log the same batch's hours twice. The answer
is 247.0.
