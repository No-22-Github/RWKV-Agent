## Traps
- TR-DATEFMT: takings/2026-07.csv mixes 03/07/2026 and 2026-07-18 styles; filtering the raw sale_date on the 2026-07 prefix drops the slash-dated days (decoy: the month filter matched the raw slash dates, so most July days dropped off)
- The scoring run also adds takings/2026-07-late.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read takings.py and its docstring: iso() normalises both date styles before aggregating.
2. Read README.md: July's file mixes day-first and ISO dates, late adjustments land as a second file for the same month.
3. Read takings/2026-07.csv to confirm the mixed styles.
4. Read takings/2026-09.csv to confirm the ISO-only files.
5. Add --month YYYY-MM: normalise every row's date first, then keep the rows whose ISO date starts with the requested month and print the month's sheet with its own TOTAL.

## Why the answer is unique
The judged month is July, whose file mixes 03/07/2026 with 2026-07-18 styles, so the flag has to normalise dates before filtering; matching the raw sale_date on the 2026-07 prefix keeps only the two ISO days and prints a two-line sheet. The README also states that late adjustments land as a second file for the same month, so the hidden takings/2026-07-late.csv contributes 2026-07-05 and the 1330 on 2026-07-18, pinning the sheet at six day lines ending TOTAL,45485.
