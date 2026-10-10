## Traps
- TR-DECOY: 邵宇航、韩佳宁各出现在两条待办里，只能改中间两条。
- replace_lines must cover the whole run of 2 lines (start_line 8, end_line 9) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 会议/周会-0914.md; the target lines are 8-9.
2. replace_lines start_line 8, end_line 9 with:
   - [ ] 魏子轩：对接物流对账，周三前
   - [ ] 邵宇航：更新报价表，下周一前
3. Read 会议/周会-0914.md back to confirm.
Final answer, one sentence: 已改 会议/周会-0914.md 第 8–9 行，共 2 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
