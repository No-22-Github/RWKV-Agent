## Traps
- TR-NEARNAME: readings/ carries Alder Walk and Alder Walk North side by side. A startswith/prefix match for "Alder Walk" folds the North plot in and prints 1280 instead of 860.

## Reference solution
1. Read watering.py: the totals and their layout are already right.
2. Read readings/2026-09.csv: Alder Walk and Alder Walk North both appear.
3. Add the --plot flag matching full names only, printing the matching plot's line alone; the no-flag behavior stays exactly as it is.

## Why the answer is unique
With full-name matching, the merged run (the scoring run adds readings/2026-10.csv) prints the single line Alder Walk,860 - 320 + 280 from September and 260 from October. The prompt pins the flag to the plot's full name, so folding Alder Walk North (another 420 litres) in contradicts the billing rule the README states; a line with the TOTAL line or extra plots differs from the expected stdout, and the no-flag behavior stays byte-identical.
