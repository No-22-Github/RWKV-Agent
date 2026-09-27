## Traps
- TR-HEADER: the export ends with a Q3-TOTAL line dated 2026-09-30 carrying the whole quarter's
  net weight (17389.0). A reader who sums every September-dated row without leaving that line out
  gets 24206.2 instead of 6817.2.

## Reference solution
1. List the workspace: the intake log and a readme.
2. Read README.md: the final line rolls up the quarter and is not a load.
3. Read intake_log_2026Q3.csv, keep the September load rows, and total net_kg: 6817.2.

## Why the answer is unique
The decoy 24206.2 adds the quarter roll-up on top of the September loads, counting part of the
quarter's weight twice. The readme says that line is not a load, and every real load has its own
load_id and grade while the roll-up reads ALL GRADES, so there is no reading in which it belongs
to September's received weight. The answer is 6817.2.
