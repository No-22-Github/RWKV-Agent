## Traps
- TR-DECOY: 早班和中班的最少人数都是 3，按 `最少人数: 3` 全文查找会先命中早班。
- replace_lines must cover the whole run of 3 lines (start_line 7, end_line 9) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 排班/规则.yaml; the target lines are 7-9.
2. replace_lines start_line 7, end_line 9 with:
       开始: "15:00"
       结束: "23:00"
       最少人数: 4
3. Read 排班/规则.yaml back to confirm.
Final answer, one sentence: 已改 排班/规则.yaml 第 7–9 行，共 3 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
