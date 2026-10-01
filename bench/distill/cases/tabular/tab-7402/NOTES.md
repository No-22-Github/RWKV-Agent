## Traps
- TR-DECOY: in invoices/billing_export.csv the August 2026 EMEA slice holds 11 rows, 5 of them Team and 3 of them Team Plus; the two plan names look alike and the amounts sit in the same range. Filtering by region and month only, without the plan, gives 13098.63 - the handiest wrong answer. The task asks for the Team plan, whose 5 rows sum to 5507.26.

## Reference solution
1. Aggregate: {{"path":"invoices/billing_export.csv","filter":{{"plan":"Team","region":"EMEA","billing_month":"2026-08"}},"operation":"sum","field":"amount_usd"}} gives 5507.26.
2. Reply with the number 5507.26 only.

## Why the answer is unique
The decoy 13098.63 adds the Team Plus, Starter and Enterprise invoices of the same August EMEA slice, but the task names the Team plan only, so those rows do not qualify. Rows from other months fail the billing_month filter. The answer is 5507.26.
