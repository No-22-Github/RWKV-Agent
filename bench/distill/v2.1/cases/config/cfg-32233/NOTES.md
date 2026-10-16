## Traps
- TR-MISSING: ~20% have no retry block.

## Reference solution
1. jq -s over conf/*.json select (.retry.max//0)>3 | length.
Reference commands (replayed in the sandbox): jq -s 'map(select((.retry.max//0)>3))|length' conf/*.json
Final answer: turn 1 -> 42 

## Why the answer is unique
Strict greater than 3.
