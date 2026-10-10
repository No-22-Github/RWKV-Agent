## Traps
- TR-AMBIG: the request names the main meter while readings/september-2026.csv holds two candidates, New Court and Old Court. Reading it as Old Court gives 3042.9; the request was settled on New Court, giving 3187.6 (from readings/september-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the main meter but the workspace holds two candidates, New Court and Old Court, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds readings/september-2026.csv and README.md.
3. read README.md: reads are weekly and each building reports on its own.
4. read readings/september-2026.csv, keep the New Court rows for the Main meter, and take the reading on the final read date of September 2026: 3187.6.

## Why the answer is unique
The decoy 3042.9 is Old Court's closing figure; it answers a different building, and the return was settled on New Court before a figure was taken.
Readings inside the month are weekly intermediate figures, not the closing one, and rows for other meters or for Old Court are out of scope. The final read date of the month pins one row for New Court, so the answer is 3187.6.

## Five alternative phrasings of the task
1. hildyard estate main meter closing reading september 2026
2. weekly readings at old court and new court
3. energy return figures per building hildyard
4. september closing figure for the main meter
5. meter readings at the two court buildings
