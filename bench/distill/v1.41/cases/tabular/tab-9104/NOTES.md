## Traps
- TR-MULTISRC: 4 per-group tables; the first alone gives 37666.37.
- TR-DECOY: 「paid-late」 contains 「paid」 as a substring; invoices/README.md says the status is matched exactly, a substring match gives 199688.40.
- TR-DEFN: aggregating every row regardless of status gives 337755.87.

## Reference solution
1. bash: `cat invoices/2026-Q3/*.csv | awk -F, '$2=="paid" {s+=$3} END{printf "%.2f\n", s}'`
Final answer: Q3 collected revenue: 133797.78 USD (state exactly `paid`; `paid-late` is excluded).

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 4 files are aggregated.

## Alternative phrasings
1. How much did we actually collect in Q3 over the four regions, per invoices/README.md?
2. Add up the paid invoices of emea, apac, amer and latam for Q3 (USD).
3. Total of all rows in state paid across the invoice exports? README has the rule.
4. Per the README, what is Q3 collected revenue in dollars?
5. Sum the amount of paid invoices in the four Q3 region files.
