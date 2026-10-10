## Traps
- TR-DECOY: 三个备份段的键完全相同，行号范围必须落在业务库那一段的前三行。
- replace_lines must cover the whole run of 3 lines (start_line 8, end_line 10) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 运维/备份计划.ini; the target lines are 8-10.
2. replace_lines start_line 8, end_line 10 with:
   周期 = 每周
   时间 = 01:45
   保留份数 = 10
3. Read 运维/备份计划.ini back to confirm.
Final answer, one sentence then DONE on its own line: 已改 运维/备份计划.ini 第 8–10 行，共 3 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
