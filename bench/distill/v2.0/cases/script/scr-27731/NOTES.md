## Traps
- TR-NUMFMT: bars/*.csv writes takings like 8,240; int() on the raw cell crashes (decoy: ValueError from int() on the comma amounts)
- The scoring run also adds bars/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read bar_totals.py: pandas only strips the separators from takings_pence, groups by bar and sums.
2. Read bars/2026-09.csv to confirm the separator amounts.
3. Rewrite bar_totals.py with csv + glob: strip commas from takings_pence, print per bar a count and a pence sum in name order, then TOTAL.

## Why the answer is unique
The amounts carry separators, so the rewrite has to strip them: Ivory Bar sums to 35835 over four sales, Foyer Bar to 7835 over two, and the hidden October export lifts the sheet to TOTAL,8,56625. The pandas version's groupby sorts bar names, so the byte-exact report leaves no other order.
