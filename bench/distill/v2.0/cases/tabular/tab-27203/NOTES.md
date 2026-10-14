## Traps
- TR-NEARNAME: the sheet also stocks RLC-4147 (425 units at GBP 2.95 — the transposed code) and RLC-4417A (155 units at GBP 4.10 — the assortpack variant), both in the visible top half of the sheet. Pricing either near-name's position gives 1253.75 or 635.50; the answer needs the row whose first column is exactly RLC-4417 (610 units at GBP 3.42, consolidated at Marsden, in the tail beyond a whole-file read).

## Reference solution
1. Read README.md: one consolidated row per stock code, the trailing-A variant rule, and that a position is the row whose first column equals the code.
2. Sample the sheet head with a line window to fix the tab-separated column order.
3. Search the exact code RLC-4417 — one row, line 987 of the sheet.
4. Read that row's window: 610 on hand at GBP 3.42.
5. Value at cost = 610 x 3.42 = 2086.2.

## Why the answer is unique
README.md states the sheet is one consolidated row per code, so "the RLC-4417 position" is exactly the row whose first column equals RLC-4417; no second row carries the code. The near-names are distinct products under the sheet's own convention (the trailing A marks a separately stocked variant; the transposed four digits are a different kit), so their rows cannot be the position asked for. Value at cost is defined by the prompt as units on hand times unit cost, giving 610 x 3.42 = 2086.2, and no other row can enter the product.
