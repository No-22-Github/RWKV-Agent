## Traps
- TR-DECOY: the entitlements table lists study leave twice, `Study leave - field engineer` at 7 days and `Study leave - laboratory technician` at 3 days. A solver that takes the first study-leave row in the file reports 7 instead of the laboratory technician's 3.

## Reference solution
1. Read README.md: the table lists one row per entitlement, and study leave names the staff group on the row.
2. Read handbook/entitlements.csv: the `Study leave - laboratory technician` row carries `days` 3; the 7 belongs to the field engineer row. The answer is 3.

## Why the answer is unique
Each entitlement row names its staff group, so the only row that answers for laboratory technicians is the one that says so, carrying 3. The decoy 7 is the field engineer's study leave, a different group on a sibling row, and the 6, 10 and 1 belong to compassionate leave, the carry-over cap and the volunteer day; reading across to the wrong group's row is the mistake the case is built around. The answer is 3.
