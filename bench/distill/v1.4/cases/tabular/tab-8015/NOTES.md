## Traps
- TR-DECOY: the rates file also has USD_CNY 7.1186 and GBP_CNY; using the USD rate on the euro total gives 42235.72.

## Reference solution
1. Read invoices/sept.csv: EUR invoices EU-2209 1840.00, EU-2214 965.40, EU-2231 3127.75 (total 5933.15 EUR).
2. Read rates/fx-2026-09.json: EUR_CNY 7.8342.
3. calculator: (1840.00 + 965.40 + 3127.75) * 7.8342, precision 2 = 46481.48.
Final answer, one sentence: the three September EUR invoices (EUR 5933.15) come to CNY 46481.48 at 7.8342. Criteria: contains the CNY total (trailing zero and thousands separator optional); calculator used.

## Why the answer is unique
Three rows are EUR; the file gives one EUR_CNY rate for the month.
