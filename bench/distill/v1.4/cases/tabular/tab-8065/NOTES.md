## Traps
- the 55% and 12% appear only in the README; list-price revenue alone is the wrong base

## Reference solution
1. Read sales/README.md: net receipts = 55% of list; royalty = 12% of net receipts.
2. data_query: hardcover rows, sum copies*list_price.
3. calculator: sum * 0.55 * 0.12, precision 2 = 9699.69.
Final answer：Hardcover royalty is $9699.69: list-price revenue x 55% net receipts x 12%.。判据：contains 9699.69 (thousands separator / trailing zeros optional), calculator used。

## Why the answer is unique
README fixes both percentages; hardcover filter is exact.
