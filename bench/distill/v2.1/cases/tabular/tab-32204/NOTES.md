## Traps
- TR-DECOY: BK-1200 and BK-120X start with BK-120.

## Reference solution
1. jq -s flatten items, select exact sku, add qty.
Reference commands (replayed in the sandbox): jq -s '[.[].items[]|select(.sku=="BK-120")|.qty]|add' library/loans-2026-09.jsonl
Final answer: turn 1 -> 921 

## Why the answer is unique
Exact sku match on nested array items.
