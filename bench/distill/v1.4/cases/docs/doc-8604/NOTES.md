## Traps
- TR-DECOY: 住宿部分同样是三行一组，且打车上限 80 与其他数字相近。
- replace_lines must cover the whole run of 3 lines (start_line 9, end_line 11) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 制度/差旅报销.md; the target lines are 9-11.
2. replace_lines start_line 9, end_line 11 with:
   高铁二等座据实报销，商务座须提前审批。
   飞机经济舱据实报销，须提前 7 天订票。
   市内打车每次不超过 100 元。
3. Read 制度/差旅报销.md back to confirm.
Final answer, one sentence then DONE on its own line: 已改 制度/差旅报销.md 第 9–11 行，共 3 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
