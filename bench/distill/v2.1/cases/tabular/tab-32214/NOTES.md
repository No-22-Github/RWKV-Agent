## Traps
- TR-MISSING: errors is absent on ~45% of lines and empty on ~20%.

## Reference solution
1. jq -s map((.errors//[])|length)|add.
2. Turn 2: count lines with non-empty errors.
Reference commands (replayed in the sandbox): jq -s 'map(select((.errors//[])|length>0))|length' trace/spans.jsonl
Final answer: turn 1 -> 539 ; turn 2 -> 213 

## Why the answer is unique
Array lengths summed; absent field counts as zero.
