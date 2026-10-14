## Traps
- TR-DECOY: meeting/minutes-0402.txt 里已办结的 A-29 与行动项条目同格式同编号段，容易被一起数进去。 A careless pass reports `A-29`.

## Reference solution
1. List meeting/ to find the export.
2. Read README.md for the 已办结 marker convention.
3. Read meeting/minutes-0402.txt, keep the 行动项 lines, and answer with one line per item.

## Why the answer is unique
A-29 is introduced by 已办结 and the README states that prefix marks completed entries kept for reference only, so it is not outstanding. Every line starting with 行动项 carries exactly one A-number and an owner, and the trailing conference note line carries neither, so the unfinished set is A-31, A-32, A-33.
