## Traps
- TR-DECOY: grouping May sales by plant_family, the family with the most orders is Herb (the cheapest line), whose total is 1062.56. The task asks for the family that sold the most money, which is Perennial.

## Reference solution
1. read_file README.md: sales is the line total per order line.
2. data_query: {"path":"data/plant_sales.tsv","filter":{"order_month":"2026-05"},"group_by":"plant_family","operation":"sum","field":"sales"} -> four group totals; the largest is Perennial with 3277.61.
3. Reply with the number 3277.61 only.

## Why the answer is unique
The decoy 1062.56 belongs to Herb, the family with the most orders, but "sold the most" ranks money, not order counts, and Perennial's total exceeds every other group by a clear margin. April and June rows fail the month condition. The answer is 3277.61.
