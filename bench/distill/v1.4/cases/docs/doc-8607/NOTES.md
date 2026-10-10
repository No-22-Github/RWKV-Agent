## Traps
- TR-DECOY: Step 3 is identical in both sections, so searching for it finds macOS first.
- replace_lines must cover the whole run of 3 lines (start_line 9, end_line 11) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read INSTALL.md; the target lines are 9-11.
2. replace_lines start_line 9, end_line 11 with:
   1. wget https://get.example.test/acme.tar.gz
   2. tar xzf acme.tar.gz -C /usr/local/bin
   3. acme --version
3. Read INSTALL.md back to confirm.
Final answer, one sentence then DONE on its own line: Updated INSTALL.md lines 9-11 (3 lines), re-read the file to confirm. / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
