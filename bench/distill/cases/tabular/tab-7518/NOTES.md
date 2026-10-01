## Traps
- TR-SIGN: credits are stored as positive amounts. Reading them as extra income and adding them to the sales total gives 12093.58; the README states the net take takes the credits back out.
- TR-MULTISRC: the sales register alone gives 9579.15, the gross take. The credits register holds half of the reconciliation; only looking there (or only at sales) cannot produce the net.

## Reference solution
1. read_file README.md: credits are positive amounts to take back out of the sales total.
2. data_query: {"path":"data/market_sales.csv","filter":{"sale_month":"2026-08"},"operation":"sum","field":"amount"} -> 9579.15.
3. data_query: {"path":"data/market_credits.csv","filter":{"credit_month":"2026-08"},"operation":"sum","field":"amount"} -> 2514.43.
4. Subtract: 9579.15 - 2514.43 = 7064.72.
5. Reply with the number 7064.72 only.

## Why the answer is unique
The decoy 12093.58 treats positive-stored credits as income, but the README defines credits as amounts to take back out, so adding them contradicts the file's own semantics. The decoy 9579.15 is the gross sales total; the question asks for the net after credits, which by definition needs both registers. July and September rows fail the month filters. The answer is 7064.72.
