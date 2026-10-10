## Traps
- TR-DECOY: 两个班的科目镜像对称，容易只改一列；范围覆盖第 3、4 节两整行。
- replace_lines must cover the whole run of 2 lines (start_line 7, end_line 8) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 教务/周三课表.md; the target lines are 7-8.
2. replace_lines start_line 7, end_line 8 with:
   | 第 3 节 | 体育 | 英语 |
   | 第 4 节 | 英语 | 体育 |
3. Read 教务/周三课表.md back to confirm.
Final answer, one sentence then DONE on its own line: 已改 教务/周三课表.md 第 7–8 行，共 2 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
