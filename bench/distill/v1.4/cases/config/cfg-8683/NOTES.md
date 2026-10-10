## Traps
- TR-DECOY: The runbook keeps the outgoing production value (12, equal to the current file) and a staging value (4).

## Reference solution
1. Read the basis runbook/workers.md: the new value is 16.
2. Read config/prod.env: line 2, `WORKERS=12`, is the one to change.
3. replace_lines line 2 with `WORKERS=16`; the rest of the line stays.
4. Read config/prod.env back to confirm.
Final answer example: WORKERS in config/prod.env is now 16, the production figure effective 2026-10-01 in runbook/workers.md. / DONE
Criteria: exact target file content; output contains DONE.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
