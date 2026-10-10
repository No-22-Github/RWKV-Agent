## Traps
- TR-ABSENT: the entitlements table has no sabbatical row. The nearest long-horizon figure is the `Annual leave carry-over cap` at 10 days, and a solver that reaches for the table's largest leave figure reports 10 instead of UNKNOWN.

## Reference solution
1. Read README.md, handbook/entitlements.csv and docs/working-patterns.md.
2. The entitlements table lists the two study-leave lines, compassionate leave, the annual leave carry-over cap and a volunteer day, and no sabbatical row exists; README.md states the handbook grants exactly what the table lists and anything beyond it is agreed case by case with a director and never counts as standard, so no standard sabbatical entitlement exists in the folder.
3. Final answer in two or three sentences: name the files checked, say the entitlements table has no sabbatical row and so no standard entitlement, and point to the table's largest leave figure (the carry-over cap) as a different entitlement without quoting its figure. Scored with output_contains_any over "sabbatical", "Sabbatical" or "sabbatical leave"; output_excludes rules out UNKNOWN and the 10-day carry-over cap, so the reply names the missing entitlement instead of quoting any day count.

## Why the answer is unique
README.md states that the table is the whole standard grant, so an entitlement with no row does not exist as a standard figure. The decoy 10 is the annual leave carry-over cap, a limit on moving days between years, not a grant of leave; reading it as a sabbatical entitlement is the mistake the case is built around. The only truthful reply reports the absence: the entitlements table, README.md and the working-pattern notes were checked, no sabbatical row exists in the table, and the carry-over cap is a different entitlement whose figure is not the answer to the question.
