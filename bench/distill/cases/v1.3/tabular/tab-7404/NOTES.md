## Traps
- TR-NEARNAME (recovery case; the recovery behaviour is the test point): the prompt only says "actually pay in freight" and the register has no column named freight or shipping_cost - only the near-name pair freight_quote (booking estimate) and freight_cost (invoiced amount actually paid). Aggregating a guessed column name first fails with `field "..." is missing`; referencing a wrong column inside filter instead returns matched_rows 0. The model must recover from the error or the empty result: list the real columns with a data_query select (no operation), or peek at the header with at most one read_file inside the case budget, then re-query with freight_cost. The README pins the mapping: freight_cost is what Maple & Lath actually pays.
- Aggregating freight_quote instead gives 4048.19; the correct answer, the freight_cost total, is 3962.78.

## Reference solution
1. Read README.md: freight_quote is the estimate at booking; freight_cost is the invoiced amount after weigh-in and fuel surcharge - the amount actually paid.
2. Aggregate: {{"path":"shipping/freight_register.csv","filter":{{"destination_state":"Ohio","ship_month":"2026-09"}},"operation":"sum","field":"freight_cost"}} gives 3962.78. (If the first attempt used a guessed column name and failed, list the columns with a select query, then re-run this query.)
3. Reply with the number 3962.78 only.

## Why the answer is unique
The decoy 4048.19 sums the booking estimates, but the task asks what the shop actually paid, and the README states the paid amount is freight_cost while freight_quote is only an estimate; the two columns differ on every row, so the quote reading does not hold. Rows for other states and months fail the filter. The answer is 3962.78.
