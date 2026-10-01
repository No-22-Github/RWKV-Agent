## Traps
- TR-MULTISRC: the uplift sheet needs gates/ and huts/ together; reading only the turnstiles prints a gates-only sheet (decoy: gates-only uplift, the hut counters left out)
- The scoring run also adds gates/2026-10.csv, huts/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read uplift.py: dateutil only parses ISO dates and sorts them.
2. Read README.md: the sheet adds the gates/ and huts/ counters per date.
3. Read gates/2026-09.csv to confirm the turnstile columns.
4. Read huts/2026-09.csv to confirm the hut columns.
5. Rewrite uplift.py with csv + glob over both folders; ISO dates sort as strings, so drop dateutil entirely.

## Why the answer is unique
The docstring adds both counters per date, so 2026-09-05 prints 476 and the sheet ends TOTAL,3024 once the scoring run's October files join. Reading only gates/ never sees the hut rows and prints a different TOTAL, and the rewrite must keep both folders or the hidden huts/2026-10.csv is missed.
