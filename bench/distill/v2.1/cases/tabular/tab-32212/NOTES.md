## Traps
- TR-DEFN: students with one record are excluded even when it is high.
- TR-DUPROW: a row-level count of scores over 85 is not the answer.

## Reference solution
1. jq -s group_by student, filter length>=2 and avg>=85, length.
Reference commands (replayed in the sandbox): jq -s 'group_by(.student)|map(select(length>=2 and ((map(.score)|add)/length)>=85))|length' 成绩/records.jsonl
Final answer: turn 1 -> 18 

## Why the answer is unique
Average is exact arithmetic mean; threshold inclusive.
