## Traps
- TR-DECOY: three Host blocks share User ops / Port 22; only bastion-us may change.
- replace_lines must cover the whole run of 3 lines (start_line 8, end_line 10) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read .ssh/config.d/bastions; the target lines are 8-10.
2. replace_lines start_line 8, end_line 10 with:
       HostName 34.201.12.140
       User deploy
       Port 2222
3. Read .ssh/config.d/bastions back to confirm.
Final answer, one sentence: Updated .ssh/config.d/bastions lines 8-10 (3 lines), re-read the file to confirm. Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
