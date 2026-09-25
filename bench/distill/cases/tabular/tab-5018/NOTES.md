## Traps
- None. The log carries both months and one row per pressing run, so the comparison uses the two real totals.

## Reference solution
1. List the workspace: the pressing log and a short readme.
2. Read press_log_2026.csv and add the litres_pressed column per month: June 2026 comes to 4414 litres and
   July 2026 to 6498 litres.
3. (July - June) / June x 100 = 47.2, so the volume rose 47.2 percent.

## Why the answer is unique
The readme states one row per pressing run, so each month's total is the sum of its own rows and no run is counted
in two months. The request fixes the two months by name and both appear in the log, so there is exactly one pair
of totals to compare and the change is 47.2.

## Review 2026-09-25
The prompt now asks for the number of percent without the sign: the first batch answered `47.2%` 3/3, which is the same value but the harness reads a number with an attached `%` as text ("is not a plain number"). The value, the trap and verify.py are unchanged.
