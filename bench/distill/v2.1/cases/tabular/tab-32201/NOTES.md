## Traps
- TR-MISSING: some orders have amount null or no amount key.
- TR-DECOY: status paid_partial also starts with paid; a loose grep over-counts.

## Reference solution
1. jq -s over the file filtering status=="paid", amount // 0, add.
2. Turn 2 adds .user.vip==true.
Reference commands (replayed in the sandbox): jq -s 'map(select(.status=="paid" and .user.vip==true)|.amount//0)|add*100|round/100' data/orders-0901-0915.jsonl
Final answer: turn 1 -> 156463.85 ; turn 2 -> 54120.90 

## Why the answer is unique
status is matched exactly and null/absent amounts contribute nothing, so the sum is unique.
