## Traps
- TR-DECOY: exact answer 240; the loose reading (level and svc prefix match) gives 26.
- TR-TRUNC: the file is 114KB and 1286 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$2=="FATAL" && $3=="billing" {print NR; exit}' svc/app.txt` -> 240
Final answer: The first billing FATAL is on line 240.

## Why the answer is unique
level and svc are whole-value columns; the first matching line is unique. The README (svc/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. What is the line number of the earliest FATAL record for billing in app.txt?
2. Find the first line where level is FATAL and svc is billing.
3. Per svc/README.md, on which line does billing first report FATAL?
4. FATAL-RECOVERED and billing-cron excluded, where is the first billing FATAL?
5. Line number of the first FATAL entry logged by billing.
