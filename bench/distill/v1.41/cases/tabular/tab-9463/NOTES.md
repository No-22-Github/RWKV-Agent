## Traps
- Turn 1: exact answer 52; the loose reading (油品、支付前缀匹配) gives 117.
- Turn 2: exact answer 18; the loose reading (油品前缀匹配) gives 32.
- Turn 3: exact answer 11; the loose reading (油品前缀匹配) gives 13.
- TR-MULTISRC: 3 files; the first file alone gives 2.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 加油站/*.txt | awk '$2=="95#" && $5=="微信" {c++} END{print c+0}'` -> 52
Turn 2: bash: `cat 加油站/*.txt | awk '$2=="95#" && $5=="油卡" {c++} END{print c+0}'` -> 18
Turn 3: bash: `cat 加油站/*.txt | awk '$2=="95#" && $5=="现金" {a++} $2=="95#" && $5=="油卡" {b++} END{d=a-b; if (d<0) d=-d; print d}'` -> 11
Final answer: 现金支付与油卡支付相差 11 笔。

## Why the answer is unique
油品 and 支付 are whole-value columns of the space-separated tables. The README (加油站/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 95# 现金笔数和油卡笔数差多少？
2. 算出现金支付的笔数，再给我它和油卡支付笔数的差值。
3. 现金与油卡两种支付的 95# 笔数相差几笔？
4. 95# 现金支付比油卡支付多（或少）多少笔，取绝对值。
5. 把现金笔数减去油卡笔数，答案取绝对值是多少？
