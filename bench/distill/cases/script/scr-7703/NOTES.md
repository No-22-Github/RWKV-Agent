## Reference solution
1. Read roastlog.py and README.md: the summary lines and their order are fixed.
2. Add a --dry-run flag: with it, print the summary lines to stdout and write
   nothing; without it, keep the current behavior exactly.

## Why the answer is unique
The summary is fully determined by the merged exports: day lines
2026-09-04,30,25 / 2026-09-11,9,8 / 2026-09-18,15,13 / 2026-09-25,20,17 /
2026-10-02,11,9 / 2026-10-09,30,26 / 2026-10-16,8,7 and then TOTAL,123,105.
The prompt pins the flag semantics (the same lines to stdout, no file), and
the scoring run both passes --dry-run and adds batches/2026-10.csv, so a flag
that still writes fails the absent check on out/roast-summary.csv and a plan
hardcoded from September's rows diverges once the October export lands.

## Traps
- None declared. The hidden October export is part of the scoring contract
  (expect.run.hidden_files), not a declared trap.
