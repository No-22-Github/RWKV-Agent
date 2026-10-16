## Traps
- TR-DECOY: 冰拿铁/燕麦拿铁/焦糖拿铁 all contain 拿铁.

## Reference solution
1. jq -s flatten items, select exact name, add qty.
Reference commands (replayed in the sandbox): jq -s '[.[].items[]|select(.name=="冰拿铁")|.qty]|add' 门店/orders-0915.jsonl
Final answer: turn 1 -> 675 ; turn 2 -> 386 

## Why the answer is unique
Exact name equality on nested items.
