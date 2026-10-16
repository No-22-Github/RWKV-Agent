## Traps
- TR-DECOY: three invalid sensor spikes of 85-120 degrees top the unfiltered file.

## Reference solution
1. jq -s select valid==true, max_by temp_c.
Reference commands (replayed in the sandbox): jq -s 'map(select(.valid==true))|max_by(.temp_c)|[.device,.temp_c]|@csv' -r sensors/readings.jsonl
Final answer: turn 1 -> 50 t-10

## Why the answer is unique
Only valid==true readings; unique maximum device.
