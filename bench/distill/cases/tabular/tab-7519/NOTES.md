## Traps
- TR-MULTISRC: the firing log alone gives 199 fired pieces. The README states every fired pot went to that month's market stock, so the unsold count only exists across the two logs.

## Reference solution
1. read_file README.md: fired pots feed the same month's market; leftovers stay in the studio.
2. data_query: {"path":"data/firings.csv","filter":{"fire_month":"2026-09"},"operation":"sum","field":"pieces_fired"} -> 199.
3. data_query: {"path":"data/market_sales.csv","filter":{"sale_month":"2026-09"},"operation":"sum","field":"pieces_sold"} -> 181.
4. Subtract: 199 - 181 = 18; reply with the number 18 only.

## Why the answer is unique
The decoy 199 counts every fired piece, but the question asks what stayed unsold, and the README ties September's firing stock to September's market, so the sold pieces must come out. July and August rows fail the month filters. The answer is 18.
