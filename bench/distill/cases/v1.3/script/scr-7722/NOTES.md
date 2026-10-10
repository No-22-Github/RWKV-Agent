## Traps
- TR-SIGN: refund rows store their pence as plain positive counts (the docstring says so); the buggy script adds them, so 09-04 prints 11000 instead of 6800 and 09-11 prints 5500 instead of 3100.
- TR-DECOY: training rows (09-05 and 09-12, both 5000) look like ordinary sale rows apart from the kind column; the docstring says they are not shop takings, yet the buggy script keeps both days on the report.

Correct semantics: net = sales - refunds per day, training rows dropped, days with only training rows get no line.

## Reference solution
1. Read takings.py: the docstring says refunds come back off and training rows are not takings.
2. Read tills/2026-09.csv: refund and training rows sit beside sales.
3. Read README.md: pence is a plain positive count either way.
4. Fix takings.py: per day net sales minus refunds, drop training rows, keep the layout.

## Why the answer is unique
Netting refunds and dropping training rows, the merged run (the scoring run adds tills/2026-10.csv with a refund, a sale and a training row on 10-02) prints exactly 2026-09-03,16000 / 2026-09-04,6800 / 2026-09-10,15200 / 2026-09-11,3100 / 2026-09-17,9800 / 2026-10-01,11400 / 2026-10-02,3400 / 2026-10-08,7600 and TOTAL,73300. The docstring states both rules in the till's own terms - the drawer's movement direction and the practice till - so the gross reading and the training days are the two readings the record itself rules out; no day in the merged data nets to zero, so the day lines are fixed either way.
