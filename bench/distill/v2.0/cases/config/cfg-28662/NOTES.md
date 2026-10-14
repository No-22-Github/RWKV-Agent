## Traps
- TR-DECOY: 三档的键名一致，数值各不同；范围要正好是高级会员下面的三行。
- replace_lines must cover the whole run of 3 lines (start_line 7, end_line 9) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 配置/会员档.ini; the target lines are 7-9.
2. replace_lines start_line 7, end_line 9 with:
   月费 = 99
   折扣 = 0.88
   赠券张数 = 6
3. Read 配置/会员档.ini back to confirm.
Final answer, one sentence then DONE on its own line: 已改 配置/会员档.ini 第 7–9 行，共 3 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
