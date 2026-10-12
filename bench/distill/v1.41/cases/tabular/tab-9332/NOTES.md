## Traps
- TR-DECOY: exact answer 246631; the loose reading (供应商包含华兴、状态前缀匹配) gives 613775.
- TR-MULTISRC: 3 files; the first file alone gives 96697.

## Reference solution
Turn 1: bash: `cat 采购台账/*.dat | awk -F';' '$2=="华兴" && $3=="已付款" {s+=$4} END{print s}'` -> 246631
Final answer: 华兴已付款合计 246631 元。

## Why the answer is unique
供应商 and 状态 are whole-value columns. The README (采购台账/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 华兴这三个月已经付清的采购金额合计多少？
2. 供应商是华兴、状态是已付款的金额加起来是多少元？
3. 按说明.md，华兴（不含华兴科技）已付款总额。
4. 三个月台账中华兴已付款的金额总和。
5. 统计供应商列等于华兴且状态列等于已付款的金额元之和。
