## Traps
- Turn 1: exact answer 160; the loose reading (prefix match on job and status) gives 392.
- Turn 2: exact answer 23139; the loose reading (job prefix match includes backup-db-weekly) gives 34174.
- TR-TRUNC: the file is 91KB and 1261 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk '$2=="backup-db" && $4=="FAIL" {c++} END{print c+0}' cron/runs.txt` -> 160
Turn 2: bash: `awk '$2=="backup-db" && $4=="OK" {s+=$5} END{print s}' cron/runs.txt` -> 23139
Final answer: Successful backup-db runs took 23139 seconds in total.

## Why the answer is unique
job and status are whole-value columns. The README (cron/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Total seconds spent by OK runs of backup-db.
2. Sum the secs column for job backup-db where status is OK.
3. How many seconds did successful backup-db runs take altogether (weekly job excluded)?
4. Per cron/README.md, what is the total secs of backup-db runs with status OK?
5. Add up the durations of backup-db's OK runs in runs.txt.
