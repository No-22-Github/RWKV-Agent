## Traps
- TR-DECOY: the device with most events overall differs from the one with most errors.
- TR-MISSING: ~7% of events have no level.

## Reference solution
1. jq -r to print devices of error events, sort | uniq -c | sort -rn.
Reference commands (replayed in the sandbox): jq -r 'select(.event.level=="error")|.device' iot/events.jsonl | sort | uniq -c | sort -rn | head -3
Final answer: turn 1 -> 22 gw-01

## Why the answer is unique
Strict level==error; the winner has a clear margin over second place.
