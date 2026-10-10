## Traps
- TR-DECOY: 1.9 only changes its date; changing its status or touching 2.0/2.1 rows fails the exact match.
- replace_lines must cover the whole run of 2 lines (start_line 5, end_line 6) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read SUPPORT.md; the target lines are 5-6.
2. replace_lines start_line 5, end_line 6 with:
   | 1.8 | end-of-life | 2026-09-30 |
   | 1.9 | maintenance | 2027-01-31 |
3. Read SUPPORT.md back to confirm.
Final answer, one sentence: Updated SUPPORT.md lines 5-6 (2 lines), re-read the file to confirm. Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
