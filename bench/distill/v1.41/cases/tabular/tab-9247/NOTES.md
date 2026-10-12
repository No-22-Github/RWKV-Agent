## Traps
- TR-DECOY: exact answer 96145; the loose match (前缀匹配，含商铺街) gives 146856.
- TR-MULTISRC: 4 files; the first file alone gives 26697.

## Reference solution
Turn 1: bash: `cat 抄表/*.dat | awk -F';' '$2=="商铺" {s+=$3} END{print s}'` -> 96145
Final answer: 商铺合计用电 96145 度。

## Why the answer is unique
区域 is a whole-value column of the semicolon-separated tables. The README (抄表/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 商铺区域九月一共用了多少度电？
2. 四个片区里区域为商铺的度数合计是多少？
3. 按说明.md，把商铺的用电量加总。
4. 抄表数据中，商铺（不含商铺街）总共多少度？
5. 九月商铺用电量合计，单位度。
