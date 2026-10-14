## Traps
- TR-READONLY: tmp_*.csv scratch exports and notes.txt stay in inbox (inbox/README.md); a `mv inbox/*.csv processed/` moves the scratch files too.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `for f in $(ls inbox/*.csv | grep -v /tmp_); do mv "$f" processed/; done`
2. bash: `ls inbox processed`
Turn 2:
1. bash: `mv processed/q3-sales.csv processed/q3-refunds.csv inbox/`
2. bash: `ls inbox processed`
Final answers: DONE (turn 1: q3-sales, q3-refunds, q3-returns, q3-stock in processed; turn 2: q3-sales and q3-refunds back in inbox).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. File the finished exports under processed (not the scratch ones), then bring the sales and refunds files back to inbox.
2. Archive the CSVs from inbox into processed per the README, then return q3-sales and q3-refunds.
3. inbox csv -> processed, except tmp files; afterwards q3-sales.csv and q3-refunds.csv go back.
4. Shift completed exports to processed; two of them (sales, refunds) must return to inbox.
5. 把 inbox 里处理完的 csv 挪到 processed，之后再把 q3-sales 和 q3-refunds 挪回来
