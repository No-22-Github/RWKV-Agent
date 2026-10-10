## Traps
- TR-DECOY: level: INFO / format: short appear three times; only the file handler's block (lines 7-9) changes.
- replace_lines must cover the whole run of 3 lines (start_line 7, end_line 9) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read logging.yaml; the target lines are 7-9.
2. replace_lines start_line 7, end_line 9 with:
       level: DEBUG
       format: json
       path: /var/log/app/debug.log
3. Read logging.yaml back to confirm.
Final answer, one sentence then DONE on its own line: Updated logging.yaml lines 7-9 (3 lines), re-read the file to confirm. / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
