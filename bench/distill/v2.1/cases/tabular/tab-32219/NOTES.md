## Traps
- TR-DEFN: order amount is the sum of qty*price over lines, not the max price.

## Reference solution
1. jq map({o:.order,t:([.lines[]|.qty*.price]|add)}) sort desc.
Reference commands (replayed in the sandbox): jq '[.[]|select(([.lines[]|.qty*.price]|add)>2500)]|length' shop/orders.json
Final answer: turn 1 -> 7538 O-3254; turn 2 -> 139 

## Why the answer is unique
Unique maximum order total; strict greater-than threshold.
