## Traps
- TR-DECOY: counting changed plus added gives a bigger number.

## Reference solution
1. jq: compare entries of both objects; keys difference for new SKUs.
Reference commands (replayed in the sandbox): jq -n --slurpfile o price/old.json --slurpfile n price/new.json '$n[0]|keys-($o[0]|keys)|(.[]),length' -r
Final answer: turn 1 -> 10 ; turn 2 -> 6 Q1001 Q1011 Q1013 Q1018 Q1020 Q1022

## Why the answer is unique
Common keys with different values; new keys.
