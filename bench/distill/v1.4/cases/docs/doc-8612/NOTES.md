## Traps
- TR-DECOY: 第五条后两句与第四条后两句逐字相同，按句子查找会命中第四条或第五条各一次。
- replace_lines must cover the whole run of 3 lines (start_line 4, end_line 6) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 合同/服务合同.md; the target lines are 4-6.
2. replace_lines start_line 4, end_line 6 with:
   甲方应在验收后 30 日内付款。
   逾期按日万分之三计违约金。
   违约金总额不超过合同金额 5%。
3. Read 合同/服务合同.md back to confirm.
Final answer, one sentence then DONE on its own line: 已改 合同/服务合同.md 第 4–6 行，共 3 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
