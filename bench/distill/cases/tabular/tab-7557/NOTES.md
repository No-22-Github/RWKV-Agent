## Traps
- TR-NEARNAME (recovery case, the recovery behaviour is the point): the prompt only says "the charges that were finally invoiced"; no column is called that. The charges file keeps a near-name pair, quote_total (the drop-off estimate) and settled_total (the amount finally invoiced that the statement is worked out from). A first aggregate over a guessed column name fails with an error like `field "..." is missing`; a filter over a missing column returns matched_rows 0. The model recovers: issue one data_query without operation and select to list the real headers (or spend the single allowed read_file on the header), then re-query with settled_total. README states the statement uses settled_total.
- Aggregating quote_total instead gives a gap of 2049.34; the correct answer is 2349.37.

## Reference solution
1. Read README.md: the statement is worked out from settled_total, not the quote.
2. Query one: {"path":"data/charges_2026-09.csv","operation":"sum","field":"settled_total"}, giving 23370.07. (If the first guessed column errors: send one data_query without operation and select to see the headers, then re-query.)
3. Query two: {"path":"data/payments_2026-09.csv","operation":"sum","field":"amount_gbp"}, giving 21020.70.
4. Subtract: 2349.37; final answer is that number alone.

## Why the answer is unique
The decoy 2049.34 is the gap against quote_total, but README ties the statement to settled_total and the two columns differ on most rows, so answering from the quote does not hold up. The answer is 2349.37 alone.
