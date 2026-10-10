## Traps
- TR-NEARNAME (recovery case; the recovery behaviour is the test point): the prompt says "actually charged", and the register has no column named charge or billed_amount - only the near-name pair estimate_amount (quoted at drop-off) and final_amount (on the invoice). Aggregating a guessed column name first fails with `field "..." is missing`; a wrong column inside filter returns matched_rows 0. The model must recover from the error or the empty result: list the real columns with a select query (no operation), or peek at the header with the single read_file the case budget allows, then re-query with final_amount. The README pins the mapping: final_amount is what the clinic actually charges.
- Aggregating estimate_amount instead gives 6089.46; the correct answer, the final_amount total, is 6268.85.

## Reference solution
1. read_file README.md: final_amount is the invoiced amount; estimate_amount is only the drop-off quote.
2. data_query: {"path":"data/service_charges.csv","filter":{"visit_month":"2026-09","species":"Dog"},"operation":"sum","field":"final_amount"} -> 6268.85. (If the first attempt guessed a column name and failed, list the columns with a select query, then re-run this query.)
3. Reply with the number 6268.85 only.

## Why the answer is unique
The decoy 6089.46 sums the drop-off quotes, but the task asks what the clinic actually charged, and the README states the charged amount is final_amount while estimate_amount is only a quote; the two columns differ on every row, so the quote reading does not hold. Cat and rabbit rows, and other months, fail the filter. The answer is 6268.85.
