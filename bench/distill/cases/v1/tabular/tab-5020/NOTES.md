## Traps
- None. One row per load, four hauliers, and the invoice asks only for the loads one haulier brought in.

## Reference solution
1. List the workspace: the August weighbridge ticket file and a short readme.
2. Read weighbridge_2026-08.csv and keep the rows whose haulier is Padstow Tippers: eight loads.

## Why the answer is unique
The readme states one row per load weighed out, and every Padstow Tippers row is a separate ticket with its own
ticket_id and tonnage, so counting those rows gives the loads that haulier brought in. No other haulier's rows
carry the name, and no row is a repeat of another, so the count is 8.
