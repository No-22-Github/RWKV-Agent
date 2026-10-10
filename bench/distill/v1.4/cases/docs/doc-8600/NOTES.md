## Traps
- TR-DECOY: A4 和 A3 行只差尺寸，必须只覆盖最后两条数据行。
- replace_lines must cover the whole run of 2 lines (start_line 7, end_line 8) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read docs/打印价目.md; the target lines are 7-8.
2. replace_lines start_line 7, end_line 8 with:
   | A3 黑白 | 0.90 | 5 |
   | A3 彩色 | 3.50 | 5 |
3. Read docs/打印价目.md back to confirm.
Final answer, one sentence then DONE on its own line: 已改 docs/打印价目.md 第 7–8 行，共 2 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
