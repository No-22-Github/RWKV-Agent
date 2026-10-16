## Traps
- TR-MISSING: some amounts are null.

## Reference solution
1. jq group_by status and sum, sort, prepend header, write file; report the count of statuses.
Reference commands (replayed in the sandbox): jq -rs 'map(select(.amount!=null))|group_by(.status)|map("\(.[0].status),\(map(.amount)|add)")|.[]' orders/day.jsonl | sort | sed '1i status,total' > orders/summary.csv; wc -l < orders/summary.csv; cat orders/summary.csv
Final answer: turn 1 -> 4 

## Why the answer is unique
Exact file content is determined by the stated format.
