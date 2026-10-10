## Traps
- TR-DECOY: [pool.read] and [pool.write] are identical, so the first match of `max = 10` is the wrong block.
- replace_lines must cover the whole run of 3 lines (start_line 7, end_line 9) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read db/pools.toml; the target lines are 7-9.
2. replace_lines start_line 7, end_line 9 with:
   min = 4
   max = 24
   idle_timeout = "15s"
3. Read db/pools.toml back to confirm.
Final answer, one sentence then DONE on its own line: Updated db/pools.toml lines 7-9 (3 lines), re-read the file to confirm. / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
