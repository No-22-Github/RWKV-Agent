## Traps
- TR-DEFN: README defines the stall report - house_account=Y standing orders are not stall sales, so they stay out. Ranking May lines without the house_account condition gives 1869.12 as the top total.

## Reference solution
1. read_file README.md: house-account lines stay out of the stall report.
2. data_query: {"path":"data/stall_sales.csv","filter":{"order_month":"2026-05","house_account":"N"},"group_by":"product_line","operation":"sum","field":"sales"} -> four group totals; the largest is Bouquets with 1388.1.
3. Reply with the number 1388.1 only.

## Why the answer is unique
The decoy 1869.12 folds the hotel standing orders into the ranking, but the task asks for the stall report ranking, and the README states house-account lines are not stall sales, so no reading keeps them. April and June rows fail the month condition. The answer is 1388.1.
