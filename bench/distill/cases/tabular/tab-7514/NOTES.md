## Traps
- TR-DECOY: grouping June sales by drink_line, the line with the most tickets is Cold Brew (the cheapest line), whose total is 825.18. The task asks for the line that earned the most money, which is Oat Latte.

## Reference solution
1. read_file README.md: sales is the line total per ticket line.
2. data_query: {"path":"data/cafe_register.csv","filter":{"sale_month":"2026-06"},"group_by":"drink_line","operation":"sum","field":"sales"} -> four group totals; the largest is Oat Latte with 1550.07.
3. Reply with the number 1550.07 only.

## Why the answer is unique
The decoy 825.18 belongs to Cold Brew, the line with the most tickets, but "earned the most" ranks money, not ticket counts, and Oat Latte's total exceeds every other group by a clear margin. May and July rows fail the month condition. The answer is 1550.07.
