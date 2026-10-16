## Traps
- TR-DECOY: /v2/checkout/retry and /v2/checkout-status share the prefix.
- TR-MISSING: about 15% of lines have no latency_ms.

## Reference solution
1. jq -s filter on exact path and status>=500, length.
2. Turn 2 adds (.latency_ms//0)>800.
Reference commands (replayed in the sandbox): jq -s 'map(select(.path=="/v2/checkout" and .status>=500 and (.latency_ms//0)>800))|length' edge/access-0914.jsonl
Final answer: turn 1 -> 21 ; turn 2 -> 11 

## Why the answer is unique
Exact path, numeric status and numeric latency comparison; absent latency cannot exceed 800.
