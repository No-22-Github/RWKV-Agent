## Traps
- None. One row per wing and week, plain integer counts.

## Reference solution
1. Turn 1: list_files to find the attendance file.
2. read visitors/attendance-2026.csv and add the Horology rows whose week ending falls in June: 205 + 232 + 214 + 189 = 840.
3. Turn 2 needs no further call: the same read holds the Ceramics June rows, 176 + 191 + 164 + 139 = 670, so the assistant answers from context.

## Why the answer is unique
Both turns concern June, fixed by the first question. The file has one row per wing and week ending, so June means the four weeks ending 2026-06-07 through 2026-06-28; the 31 May row is a May week and stays out. Each June wing sum is therefore fixed: Horology 205 + 232 + 214 + 189 and Ceramics 176 + 191 + 164 + 139.

## Five alternative phrasings of the task
1. greystoke museum horology wing june visitors
2. ceramics wing attendance june 2026
3. greystoke weekly admissions spring
4. how many visitors did each wing get in june
5. greystoke museum door count june weeks
