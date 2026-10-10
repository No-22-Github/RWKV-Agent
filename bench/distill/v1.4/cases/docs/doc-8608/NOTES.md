## Traps
- TR-DECOY: 孟思远在四行里都出现，只有 10-02 的夜班和 10-03 的白班要换，两行内另一人的名字保持。
- replace_lines must cover the whole run of 2 lines (start_line 6, end_line 7) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 值班/国庆.md; the target lines are 6-7.
2. replace_lines start_line 6, end_line 7 with:
   | 10-02 | 柴雪晴 | 容嘉树 |
   | 10-03 | 容嘉树 | 柴雪晴 |
3. Read 值班/国庆.md back to confirm.
Final answer, one sentence: 已改 值班/国庆.md 第 6–7 行，共 2 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
