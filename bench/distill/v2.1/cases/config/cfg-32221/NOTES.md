## Traps
- TR-DECOY: counting enabled flags in every group gives a larger number.

## Reference solution
1. jq recursive descent over objects that have enabled.
Reference commands (replayed in the sandbox): jq '[.payments.flags|..|objects|select(has("enabled") and .enabled==true and .owner=="b")]|length' config/flags.json
Final answer: turn 1 -> 23 ; turn 2 -> 5 

## Why the answer is unique
Leaf flags are objects with an enabled key; the group rollout number is not a flag.
