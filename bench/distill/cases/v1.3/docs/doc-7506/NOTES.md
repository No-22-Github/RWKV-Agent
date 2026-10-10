## Traps
- TR-DECOY: policies/refund-windows.csv 同时有 Premium（45 天）与 Premium annual（60 天）两行，粗读会取 45 天那行。 A careless pass reports `45`.

## Reference solution
1. List policies/ to find the window table and the policy page.
2. Read policies/refund-windows.csv and locate the Premium annual row.
3. Read policies/refund-policy.md to confirm the annual-contract rule, then answer.

## Why the answer is unique
The table has a dedicated Premium annual row, and the policy page says the window follows the tier recorded for the return, so the plain Premium row (45 days, original payment) does not apply. The Premium annual row gives 60 days and store credit, matching the annual-contract rule, so both readings agree on one answer.
