## Traps
- TR-DECOY: The log holds three visits with three set points; -20 is the current file value and -22 an intermediate one.

## Reference solution
1. Read the basis maintenance/freezer-visits.log: the new value is -21.
2. Read config/freezer-3.toml: line 3, `setpoint_c = -20`, is the one to change.
3. replace_lines line 3 with `setpoint_c = -21`; the rest of the line stays.
4. Read config/freezer-3.toml back to confirm.
Final answer example: config/freezer-3.toml now has setpoint_c = -21, from the 2026-09-05 visit that supersedes the earlier ones.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
