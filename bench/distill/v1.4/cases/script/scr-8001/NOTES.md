## Traps
- glob only matches the top level of sales/, so the two August weekly files are skipped.

## Reference solution
1. Read dish_tally.py. 2. List sales/ (subfolder 2026-08). 3. replace_lines the glob line with a recursive glob. 4. Read back. Final: one sentence.

## Why the answer is unique
Recursive glob picks up every csv under sales/ including nested month folders.
The fixed script prints:
清蒸鱼 27
红烧肉 87
麻婆豆腐 63
