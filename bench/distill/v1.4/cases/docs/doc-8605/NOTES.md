## Traps
- TR-DECOY: A second table (response headers) uses the same three columns; only the query parameter rows change.
- replace_lines must cover the whole run of 2 lines (start_line 7, end_line 8) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read docs/api/list.md; the target lines are 7-8.
2. replace_lines start_line 7, end_line 8 with:
   | sort | string | updated |
   | order | string | asc |
3. Read docs/api/list.md back to confirm.
Final answer, one sentence: Updated docs/api/list.md lines 7-8 (2 lines), re-read the file to confirm. Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
