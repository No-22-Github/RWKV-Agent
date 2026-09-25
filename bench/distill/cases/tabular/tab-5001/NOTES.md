## Traps
- TR-DUPROW: exports/shipments_2026-08.csv repeats HX-40215 and HX-40217 (both Canada) and HX-40218 (United States). Counting Canada rows instead of orders gives 7.

## Reference solution
1. List the workspace to find the export and README.
2. Read README.md: the export job retried, so rows can repeat.
3. Read exports/shipments_2026-08.csv, keep Canada rows, count distinct order_ref: PO-88104, PO-88111, PO-88120, PO-88131, PO-88142 = 5.

## Why the answer is unique
The decoy 7 counts rows, but the question asks for orders and the README says there is one shipment per order, so the repeated rows are the same shipments written twice. Every repeated row matches its original in every column, so there is no reading in which they are separate orders. The answer is 5.
