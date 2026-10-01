# fs-8004 (p13 holdout, eval-only)

## Traps
- TR-NEARNAME: the guide mentions stockroom-log.txt (the pre-August location, retired) before it names the current logs/restock-log.txt. A model that grabs the first concrete path and appends there creates a file the `absent` expectation rejects, while the real log stays without the three lines. The two source files are pinned byte-for-byte. `trap_decoys` is null: the wrong outcome is a file state, not a single value.

## Reference solution
1. Read stock/current.csv and compare on_hand against the reorder points (ref call 1).
2. Read stock-guide.md for the reorder points, the order quantities and where restock lines go (ref call 2).
3. Read logs/restock-log.txt for the line form and its last line (ref call 3).
4. Append three lines in CSV row order - oat-flour-1kg x24, rye-flour-1kg x18, spelt-flour-1kg x12, all dated 2026-09-24 (ref call 4).

## Why the answer is unique
oat (9 < 12), rye (26 < 30) and spelt (6 < 10) are below their reorder points; barley (41) and wheat (57) are not. The prompt fixes the date, the CSV row order and the line form (`YYYY-MM-DD RESTOCK <sku> x<qty>` as in the existing entries), so the appended block is exactly those three lines in that position. The end-anchor needle requires the first new line to sit directly under the 2026-09-19 entry (no blank line, no middle insert), the adjacency needles pin the row order, and the `absent` check rejects the retired stockroom-log.txt.
