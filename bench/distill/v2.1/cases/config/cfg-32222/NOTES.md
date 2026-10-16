## Traps
- TR-DECOY: counting every host per zone gives a larger number.

## Reference solution
1. jq -r select prod web, print az; sort | uniq -c | sort -rn.
Reference commands (replayed in the sandbox): jq -r '.hosts[]|select(.tags.env=="prod" and .tags.role=="web" and .az!=null)|.az' infra/inventory.json | sort | uniq -c | sort -rn | head -3
Final answer: turn 1 -> 19 us-east-1b

## Why the answer is unique
Filter by both tags; unique winner by margin.
