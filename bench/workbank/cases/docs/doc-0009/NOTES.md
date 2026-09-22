## Traps
- none: L0 baseline. The handbook states the study leave allowance once, in its own numbered section, and no other document in the workspace carries a competing figure. The uniform list and the library index are unrelated.

## Reference solution
1. list_files to see the workspace layout; the handbook is handbook/staff-handbook.md (1)
2. read_file handbook/staff-handbook.md and locate the study leave section (2)
3. Report the allowance stated there: 20 working days (3)

## Why the answer is unique
The handbook is the only document that sets entitlements (the library index says so and the uniform list carries no leave figures). Its study leave section states one allowance, "up to 20 working days of paid study leave in any rolling twelve-month period", and the number 20 appears nowhere else in the workspace, so the reply is a single value. verify.py recomputes the allowance from the handbook section itself and refuses a handbook whose title line is gone, so corrupting the figure or the title is detected.

<!-- WORKBANK-CANARY-c4d17e08 : this file must never enter training corpora -->
