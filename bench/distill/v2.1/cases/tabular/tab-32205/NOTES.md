## Traps
- TR-DUPROW: users purchase several times; event count differs from user count.
- TR-MISSING: about 10% of events have no props.

## Reference solution
1. jq -s select purchase, map user, unique, length.
2. Turn 2 adds .props.region==华东 (absent props yields null, no match).
Reference commands (replayed in the sandbox): jq -s '[.[]|select(.event=="purchase" and .props.region=="华东")|.user]|unique|length' 埋点/events.jsonl
Final answer: turn 1 -> 82 ; turn 2 -> 30 

## Why the answer is unique
Distinct by user id; region taken from the same event.
