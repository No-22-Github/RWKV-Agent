## Traps
- TR-DUPROW: lorry_loads_2026-08.csv writes three of the Coldborough Transport loads twice, so counting rows for that haulier gives 16 rather than the 13 loads actually taken out.

## Reference solution
1. List the workspace: the August load file and a short readme.
2. Read README.md: the office exported part of the month twice, so rows can repeat.
3. Read lorry_loads_2026-08.csv, keep the Coldborough Transport rows and count distinct load_id: 13 loads.

## Why the answer is unique
The readme says one row per load and explains that part of the month was exported twice, and each repeated row matches its original in every column including the load_id and the weight, so the repeats are the same loads written out again rather than extra loads. Counting the distinct Coldborough Transport load_id values gives 13.
