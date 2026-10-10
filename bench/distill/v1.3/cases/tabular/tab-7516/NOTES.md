## Traps
- TR-NEARNAME (recovery case; the recovery behaviour is the test point): ranking "the vehicle make with the highest total" needs the settled amount, and the register has no column named cost or billed - only the near-name pair cost_estimate (before parts are priced) and cost_final (on the settled invoice). A group_by over a guessed column first fails with `field "..." is missing` or `group_by field ... is missing`; a wrong column inside filter returns matched_rows 0. The model must recover: list the real columns with a select query (no operation), or peek at the header with the single read_file the case budget allows, then re-query with cost_final. The README pins the mapping.
- Ranking on cost_estimate instead crowns Ford with 2091.56; the correct answer, Toyota's cost_final total, is 1932.5.

## Reference solution
1. read_file README.md: cost_final is the settled invoice amount; cost_estimate is only the pre-parts figure.
2. data_query: {"path":"data/job_costs.csv","filter":{"job_month":"2026-09"},"group_by":"vehicle_make","operation":"sum","field":"cost_final"} -> five group totals; the largest is Toyota with 1932.5. (If the first attempt guessed a column name and failed, list the columns with a select query, then re-run this query.)
3. Reply with the number 1932.5 only.

## Why the answer is unique
The decoy 2091.56 ranks pre-parts estimates, but the task asks which make drove the most repair revenue, and the README states the billed amount is cost_final; the two columns differ on every row, so the estimate ranking does not hold. May, June and July rows fail the month condition. The answer is 1932.5.
