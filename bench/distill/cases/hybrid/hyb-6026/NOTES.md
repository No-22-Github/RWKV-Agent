## Traps
- None. One row per wing and week, and the May totals are far apart.

## Reference solution
1. Turn 1: list_files to find the admissions file.
2. read visitors/admissions-2026.csv, total each wing's May rows (Textiles 262 + 244 + 271 + 258 + 249 = 1284 against Ceramics 999 and Horology 859) and answer Textiles.
3. Turn 2 needs no further call: the same read fixed Textiles' May total, 1284, so the assistant answers from context.

## Why the answer is unique
May means the five weeks ending 2026-05-03 through 2026-05-31; April and June rows stay out. Textiles' 1284 leads Ceramics (999) and Horology (859) by a wide margin, so the top wing is not a judgement call, and its May sum is exactly the rows the file holds. The follow-up's 'that' can only refer to the wing named in the first answer.

## Five alternative phrasings of the task
1. which greystoke wing had the most visitors in may
2. textiles wing may attendance greystoke
3. greystoke museum may visitor totals by wing
4. top wing for may admissions greystoke museum
5. how many visitors did the textiles wing get in may
