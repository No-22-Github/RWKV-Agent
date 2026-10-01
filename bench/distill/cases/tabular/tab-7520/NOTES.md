## Traps
- TR-NEARNAME (recovery case; the recovery behaviour is the test point): "actually paid" needs the settled amount, and the register has no column named paid or cost - only the near-name pair amount_auth (the pump hold) and amount_settled (what clears). Aggregating a guessed column first fails with `field "..." is missing`; a wrong column inside filter returns matched_rows 0. The model must recover: list the real columns with a select query (no operation), or peek at the header with the single read_file the case budget allows, then re-query with amount_settled. The README pins the mapping.
- TR-MULTISRC: the charge register alone gives 6160.72. The rebates register holds the deduction; only looking there (or only at charges) cannot produce the net.

## Reference solution
1. read_file README.md: amount_settled is what actually clears; rebates are positive amounts to take back out.
2. data_query: {"path":"data/fuel_card_charges.csv","filter":{"charge_month":"2026-08"},"operation":"sum","field":"amount_settled"} -> 6160.72.
3. data_query: {"path":"data/fuel_credits.csv","filter":{"credit_month":"2026-08"},"operation":"sum","field":"credit_amount"} -> 1181.18.
4. Subtract: 6160.72 - 1181.18 = 4979.54.
5. Reply with the number 4979.54 only.

## Why the answer is unique
The decoy 5017.06 nets the pump holds instead of the settled amounts, but the README states the card is charged what clears, and the two columns differ on every row. The decoy 6160.72 ignores the rebates entirely, which the README folds into the month's fuel cost. July and September rows fail the month filters. The answer is 4979.54.
