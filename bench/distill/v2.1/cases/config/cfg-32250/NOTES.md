## Traps
- TR-TRUNC: ~120 files.

## Reference solution
1. grep team lines | sort | uniq -c | awk to JSON object.
Reference commands (replayed in the sandbox): grep -rh '^team=' owners | sed 's/team=//' | sort | uniq -c | awk 'BEGIN{printf "{"} {printf "%s\"%s\":%d", (NR>1?",":""), $2, $1} END{print "}"}' > owners/summary.json; cat owners/summary.json; grep -c team owners/summary.json; echo 3
Final answer: turn 1 -> 3 

## Why the answer is unique
Counts per team are exact; compact JSON with trailing newline.
