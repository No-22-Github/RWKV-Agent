## Traps
- TR-NUMFMT: the amount column prints as ledger amounts with a currency symbol and group separators, so column aggregation tools refuse the column outright. Reading them by eye and dropping the cents gives 7311.0 for Marleythorpe instead of 7312.1.

## Reference solution
1. Turn 1: list_files to find the June invoice run.
2. read invoices/june-2026.csv; aggregating the amount column errors out on the formatting, so the amounts are read cell by cell instead.
3. add the Marleythorpe Engineering amounts with the calculator: 2417.35 + 1204.60 + 3690.15 = 7312.10.
4. Turn 2 needs no further call: the same read holds Cotterill Farms' two amounts, 864.20 + 452.85 = 1317.05.

## Why the answer is unique
Each invoice line names one client and one amount, and every Marleythorpe line and every Cotterill line is already in the file read during turn 1. The only defensible total keeps the printed cents: dropping them quietly loses the small change on all three lines and lands on 7311.0, which matches no full reading of the amounts. Client and month are fixed by the wording, so 7312.1 and 1317.05 are the only totals the run supports.

## Five alternative phrasings of the task
1. sparrowfield fabrications marleythorpe june invoices
2. what was billed to cotterill farms in june
3. sparrowfield june invoice run by client
4. june total for marleythorpe engineering
5. sparrowfield invoice amounts june 2026
