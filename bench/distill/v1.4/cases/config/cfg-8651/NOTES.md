## Traps
- TR-DECOY: api has the same interval/timeout/retries lines at 6-8; only the worker's lines 13-15 may change.
- replace_lines must cover the whole run of 3 lines (start_line 13, end_line 15) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read docker-compose.yml; the target lines are 13-15.
2. replace_lines start_line 13, end_line 15 with:
         interval: 10s
         timeout: 3s
         retries: 5
3. Read docker-compose.yml back to confirm.
Final answer, one sentence: Updated docker-compose.yml lines 13-15 (3 lines), re-read the file to confirm. Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
