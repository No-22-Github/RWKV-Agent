## Traps
- TR-DECOY: Rows must keep Quarter in place while theme and owner move together; three rows are rewritten, Q1 is not.
- replace_lines must cover the whole run of 3 lines (start_line 6, end_line 8) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read ROADMAP.md; the target lines are 6-8.
2. replace_lines start_line 6, end_line 8 with:
   | Q2 | Offline mode | Mobile |
   | Q3 | Search relevance | Search |
   | Q4 | Billing v2 | Payments, Growth |
3. Read ROADMAP.md back to confirm.
Final answer, one sentence: Updated ROADMAP.md lines 6-8 (3 lines), re-read the file to confirm. Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
