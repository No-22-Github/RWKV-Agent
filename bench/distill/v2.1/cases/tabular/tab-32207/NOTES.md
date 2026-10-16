## Traps
- TR-MISSING: unresolved tickets have resolved_at null.
- TR-DECOY: counting every P1 or every P1 billing ticket gives other numbers.

## Reference solution
1. jq -s select priority P1 and resolved_at!=null, length.
2. Turn 2 adds the billing tag test.
Reference commands (replayed in the sandbox): jq -s 'map(select(.priority=="P1" and .resolved_at!=null and (.tags|index("billing"))!=null))|length' support/tickets.jsonl
Final answer: turn 1 -> 61 ; turn 2 -> 17 

## Why the answer is unique
Exact priority, non-null resolved_at, tag membership.
