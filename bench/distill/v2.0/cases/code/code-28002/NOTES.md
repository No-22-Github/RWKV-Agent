## Traps
- TR-DECOY: the reporting database also has `"PORT": 5432,` (line 16); it must stay at 5432.

## Reference solution
1. Read app/settings.py: the default entry's port is line 9, `        "PORT": 5432,  # direct to postgres` (8-space indent).
2. replace_lines line 9 with `        "PORT": 6432,  # pgbouncer`.
3. Read app/settings.py back to confirm indentation and that reporting is untouched.
Final answer, one sentence: default now connects on 6432 (pgbouncer) in app/settings.py line 9; reporting still goes direct on 5432. Criteria: exact file content; output contains 6432.

## Why the answer is unique
The prompt names the default database and the new comment text; indentation must be kept for valid Python, so only one resulting file is acceptable.
