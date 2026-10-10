## Traps
- TR-DECOY: 行政组出现在多行，按负责人查找容易错位；范围只有茶歇和颁奖这相邻两行。
- replace_lines must cover the whole run of 2 lines (start_line 8, end_line 9) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 活动/年会议程.md; the target lines are 8-9.
2. replace_lines start_line 8, end_line 9 with:
   | 15:50 | 茶歇 | 行政组 |
   | 16:10 | 颁奖典礼 | 工会 |
3. Read 活动/年会议程.md back to confirm.
Final answer, one sentence: 已改 活动/年会议程.md 第 8–9 行，共 2 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
