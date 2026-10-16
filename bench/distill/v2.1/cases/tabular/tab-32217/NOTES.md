## Traps
- TR-DECOY: 鸡蛋清 contains 鸡蛋; a text search over-counts.

## Reference solution
1. jq select ingredients array contains exact 鸡蛋, then add kcal.
Reference commands (replayed in the sandbox): jq '[.recipes[]|select(.ingredients|index("鸡蛋"))|.kcal]|add' 菜谱/recipes.json
Final answer: turn 1 -> 110 ; turn 2 -> 57297 

## Why the answer is unique
Exact array membership.
