## Traps
- None. The case teaches using only the three offered tools.

## Reference solution
1. Search the workspace for "round" (or list billing/ and read billing/invoice.py).
2. billing/money.py defines round_invoice_total (quantize to the cent, ROUND_HALF_UP); billing/invoice.py imports and calls it.
Final answer in one sentence: round_invoice_total in billing/money.py rounds totals to the cent, half up; invoice_total in billing/invoice.py calls it. Criteria: contains round_invoice_total and billing/money.py.

## Why the answer is unique
Only one function definition has both "round" and "invoice" in its name; round_display formats for display and does not round totals.
