## Traps
- TR-DUPROW: the retried job repeated the 09-03 web and 09-24 partner image-resize rows (17.30 + 12.40). Summing all rows gives 217.50; after dropping the repeated lines the endpoint total is 187.80 (turn 1). Mobile team rows are 24.80+31.60+24.10+17.40+8.80 = 106.70 (turn 2). Turn 3 excludes the two staging rows (5.70 + 7.40): 187.80 − 13.10 = 174.70.

## Reference solution
1. Read api-usage-2026-09.csv and the README note about the retried export (turn 1).
2. Deduplicate image-resize rows by day x team x key_type, sum cost: 187.80.
3. Filter team=mobile over the deduplicated rows: 106.70 (turn 2).
4. Drop key_type=staging rows and re-sum: 187.80 − 5.70 − 7.40 = 174.70 (turn 3).

## Why the answer is unique
The README pins the dedup key (day x team x key_type x endpoint is one line), so the two byte-identical repeats are the same billed line written twice; 217.50 has no defensible reading. Mobile and staging are exact column filters over unique rows, so 106.70 and 174.70 are unique. Answers are uniquely 187.80, 106.70, 174.70.

## Five alternative phrasings
- What did image-resize cost us in September
- Total September spend on the image-resize endpoint
- How much of that was the mobile team's
- Excluding staging keys, what is the endpoint total
- Re-run the image-resize total without staging traffic
