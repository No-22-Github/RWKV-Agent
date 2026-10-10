## Traps
- TR-NEARNAME: payment-svc appears under its legacy spelling paymentsvc in 6 rows that night (renamed on 2026-09-12 per the README). Counting only the new spelling gives 6 and hands the win to search-svc (9), which is the decoy; merged, payment-svc has 11.

## Reference solution
1. Turn 1: read README.md (paymentsvc is the same service as payment-svc), read logs/edge-access.log, merge the two spellings and count 5xx per upstream: payment-svc 11 (6 new + 5 legacy), auth-svc 9, cart-svc 2. Answer: payment-svc.
2. Turn 2: drop 5xx rows inside [03:14:00, 03:19:59] (four payment-path rows: 03:14:22, 03:15:48, 03:16:30, 03:17:14): payment-svc 7, auth-svc 10. Answer: auth-svc.
3. Turn 3: bucket all 21 5xx rows by minute: 03:34 has 4 (three search-svc at :00/:41/:52 plus cart-svc at :18), no other minute exceeds 2. Answer: 03:34.
4. Turn 4: within 03:34 the split is auth-svc 3, cart-svc 1. Answer: auth-svc.

## Why the answer is unique
The README makes the legacy spelling mandatory to merge, and no third spelling appears, so the merged counts are fixed (11 vs 10). The maintenance window is defined by exact timestamps in the prompt and its five rows are all payment-path, which is what flips the ranking; outside it the per-upstream totals are 7 vs 10. Minute bucketing is exact on the log timestamps, and 03:34 is the only minute with four 5xx rows, with a 3-1 split inside.
