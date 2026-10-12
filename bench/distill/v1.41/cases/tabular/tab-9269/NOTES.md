## Traps
- TR-READONLY: 对外报表.csv and 模板.csv keep RMB. TR-DECOY: `RMB-HK` starts with RMB (a substring `s/RMB/CNY/` turns it into CNY-HK).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find 财务 -name '2026-*.csv' | xargs sed -i 's/,RMB$/,CNY/'`
2. bash: `grep -rc CNY 财务`
Final answer: DONE (七月八月九月的 RMB 记录已改为 CNY).
Turn 2:
1. bash: `sed -i 's/,CNY$/,RMB/' 财务/2026-07.csv 财务/2026-08.csv`
2. bash: `grep -rc CNY 财务`
Final answer: DONE (七月八月又是 RMB，九月是 CNY).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 各月流水里 RMB 换成 CNY（对外报表、模板、RMB-HK 不动），之后七八月还原
2. 把币种 RMB 批量改为 CNY，然后 07 和 08 两个月再改回去
3. 财务 CSV 的币种代码迁到 CNY，七月八月撤销
4. RMB→CNY，只保留九月的修改
5. Change RMB to CNY in the monthly sheets, then undo it for July and August.
