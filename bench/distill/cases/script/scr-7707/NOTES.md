## Traps
- TR-SIGN: the refunded column stores returned plugs as plain positive counts (Ajuga 0, Erysimum 6+4, Geum 5). Adding every column or reading only the ordered column gives 260 plugs instead of the 245 that still have to go out.

## Reference solution
1. Read packlist.py: its docstring fixes the layout and the refunded rule.
2. Read orders/2026-09.csv to confirm the columns and the returns rows.
3. Read README.md: the returns shelf lands in the refunded column as plain counts.
4. Write packlist.py: aggregate ordered minus refunded per variety, print in alphabetical order, then the NET line.

## Why the answer is unique
With returns taken off, the merged orders (the scoring run adds orders/2026-10.csv with two more returns) print exactly Ajuga,60 / Erysimum,80 / Geum,69 / Tiarella,68 and NET,277. The docstring inside packlist.py pins the rule - the refunded column is a plain count on the same scale as ordered and comes back off the variety's total - so the plain ordered sum (260 in September) is the reading of a column the portal itself fills with returns; every net stays positive, so no second reading of the arithmetic exists.
