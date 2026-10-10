## Traps
- TR-DECOY: F-13 gives report-export a time too, and F-14 is about retention, not schedule.

## Reference solution
1. Read the basis audit/findings-2026-09.txt: the new value is 02:30.
2. Read ops/jobs.yaml: line 1, `- job: nightly-backup
  at: "01:00"`, is the one to change.
3. replace_lines line 1 with `- job: nightly-backup
  at: "02:30"`; the rest of the line stays.
4. Read ops/jobs.yaml back to confirm.
Final answer example: ops/jobs.yaml now schedules nightly-backup at 02:30, per audit finding F-12; report-export is untouched.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
