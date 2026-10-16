## Traps
- TR-MISSING: ~10% of lines have no currency key; adding every amount mixes HKD and USD in.

## Reference solution
1. jq -s select currency CNY, sum amount, round to 2 decimals.
Reference commands (replayed in the sandbox): jq -s 'map(select(.currency=="CNY")|.amount)|add*100|round/100' 财务/payments-0916.jsonl
Final answer: turn 1 -> 111802.76 

## Why the answer is unique
Only rows with currency exactly CNY count.
