# scr-8003 (p13 holdout, eval-only)

## Traps
- TR-DUPROW: floor1.csv repeats its 06:15 line and floor3.csv repeats its 06:30 line; summing every line gives 2856 for floor1 instead of 2458 and 2071 for floor3 instead of 1770. The README says readings are the same only when the whole line matches, and each reading counts once.
- TR-DECOY: floor2-old.csv sits in the same folder and looks like more data; the README scopes current logs to `floor<N>.csv`, so an extra `floor2-old.csv: 909` line - or its rows folded into another total - fails.
- `trap_decoys` is null: the judged value is the script's stdout over visible plus hidden inputs, not a single fixture number.

## Reference solution
1. Read README.md for the log format, the retry rule and the archive rule (ref call 1).
2. Read data/readings/floor1.csv, floor2.csv and floor3.csv (ref calls 2-4).
3. Write scripts/energy_report.py: for every floor<N>.csv in data/readings, in filename order, sum the second column over distinct lines and print "<basename>: <total>" (ref call 5).

## Why the answer is unique
The output format, the sort order, the dedup rule and the archive exclusion are all fixed by the README, so exactly one stdout satisfies the case: one line per current floor log, each the sum of that file's distinct readings. The offline run copies a hidden floor4.csv into the workspace before executing, so hard-coding the three visible files, their names or their totals fails; only a script that implements the README's rules produces the expected four lines.
