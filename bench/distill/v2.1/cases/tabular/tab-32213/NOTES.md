## Traps
- TR-DECOY: Kestrel Cafe II shares the prefix.

## Reference solution
1. jq -s exact merchant, status refunded, sum amount.
2. Turn 2: add amount>100, length.
Reference commands (replayed in the sandbox): jq -s 'map(select(.merchant=="Kestrel Cafe" and .status=="refunded" and .amount>100))|length' pay/ledger.jsonl
Final answer: turn 1 -> 7066.72 ; turn 2 -> 24 

## Why the answer is unique
Exact merchant and status strings.
