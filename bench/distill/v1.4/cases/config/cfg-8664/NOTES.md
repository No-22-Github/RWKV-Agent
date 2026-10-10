## Traps
- TR-DECOY: 长宁店与静安店的原值逐字相同。
- replace_lines must cover the whole run of 3 lines (start_line 7, end_line 9) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 配置/门店营业.yaml; the target lines are 7-9.
2. replace_lines start_line 7, end_line 9 with:
       营业开始: "10:30"
       营业结束: "20:00"
       外卖开关: 关
3. Read 配置/门店营业.yaml back to confirm.
Final answer, one sentence: 已改 配置/门店营业.yaml 第 7–9 行，共 3 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
