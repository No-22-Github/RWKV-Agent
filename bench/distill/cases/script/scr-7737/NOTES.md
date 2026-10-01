## Traps
- TR-DECOY: outbox/2026-09-draft.csv holds the office's draft with settled numbers that differ from the final export; the sheet reads consignments/ only (decoy: outbox draft rows counted into the sheet)
- The scoring run also adds consignments/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read consign.py: the docstring fixes the layout and the final-exports-only rule.
2. Read README.md: drafts wait in outbox/; the sheet reads consignments/ only.
3. Read consignments/2026-09.csv to confirm the columns.
4. Write consign.py: sweep consignments/*.csv, aggregate per sent_date, print in date order, then TOTAL.

## Why the answer is unique
The docstring and README state the sheet reads the final exports in consignments/ only; the outbox draft carries different case counts (CC-8301 as 10 against the final 12), so no reading admits it. The sheet ends TOTAL,8,85 once the scoring run's October export joins, and a script that sweeps the outbox too prints an extra 2026-09-03 row with wrong cases.
