## Traps
- TR-DECOY: CR-77 (365) was rejected; CR-82 approves a different setting (metrics, 30).

## Reference solution
1. Read the basis approvals/log-retention.txt: the new value is 120.
2. Read config/retention.env: line 1, `LOG_RETENTION_DAYS=90`, is the one to change.
3. replace_lines line 1 with `LOG_RETENTION_DAYS=120`; the rest of the line stays.
4. Read config/retention.env back to confirm.
Final answer example: LOG_RETENTION_DAYS in config/retention.env is now 120, per approved request CR-81; the rejected 365 was ignored.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
