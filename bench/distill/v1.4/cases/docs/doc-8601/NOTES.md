## Traps
- TR-DECOY: Highlights repeats the feature names (export wizard, dark theme); only the three Known issues bullets (lines 9-11) change.
- replace_lines must cover the whole run of 3 lines (start_line 9, end_line 11) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read RELEASE-3.8.md; the target lines are 9-11.
2. replace_lines start_line 9, end_line 11 with:
   - Export wizard fails on files over 4 GB
   - Tray icon blurry on 4K displays (fixed in 3.8.1)
   - Dark theme flicker fixed in 3.8
3. Read RELEASE-3.8.md back to confirm.
Final answer, one sentence then DONE on its own line: Updated RELEASE-3.8.md lines 9-11 (3 lines), re-read the file to confirm. / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
