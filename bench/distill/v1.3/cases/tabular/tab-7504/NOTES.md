## Traps
- TR-NEARNAME (recovery case; the recovery behaviour is the test point): the prompt says "actually received", and the log has no column named pay or received - only the near-name pair ot_offered (originally offered) and ot_approved (what payroll pays). Aggregating a guessed column name first fails with `field "..." is missing`; a wrong column inside filter returns matched_rows 0. The model must recover: list the real columns with a select query (no operation), or peek at the header with the single read_file the case budget allows, then re-query with ot_approved. The README pins the mapping: ot_approved is what payroll actually pays.
- Aggregating ot_offered instead gives 4797.02; the correct answer, the ot_approved total, is 3685.86.

## Reference solution
1. read_file README.md: ot_approved is what payroll actually pays; ot_offered is only the original offer.
2. data_query: {"path":"data/overtime_log.csv","filter":{"entry_month":"2026-08","task":"Hardscape"},"operation":"sum","field":"ot_approved"} -> 3685.86. (If the first attempt guessed a column name and failed, list the columns with a select query, then re-run this query.)
3. Reply with the number 3685.86 only.

## Why the answer is unique
The decoy 4797.02 sums the offered amounts, but the task asks what the crews actually received, and the README states payroll pays ot_approved while ot_offered is only the original offer; the two columns differ on every row, so the offered reading does not hold. Other tasks and months fail the filter. The answer is 3685.86.
