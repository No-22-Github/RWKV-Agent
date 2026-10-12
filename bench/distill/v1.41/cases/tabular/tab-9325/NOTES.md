## Traps
- TR-DECOY: exact answer 73190; the loose reading (忽略大小写，含API) gives 111993.
- TR-MULTISRC: 3 files; the first file alone gives 25452.

## Reference solution
Turn 1: bash: `cat 云账单/*.txt | awk -F, '$2=="api" {s+=$4} END{print s}'` -> 73190
Final answer: 项目 api 三个月合计 73190 元。

## Why the answer is unique
项目 is a case-sensitive whole-value column. The README (云账单/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 小写 api 项目这三个月花了多少钱？
2. 云账单里项目名恰好是 api 的费用加起来是多少元？
3. 按说明.md，api（不含 API）的费用总额是多少？
4. 统计项目列等于 api 的费用元之和。
5. 8、9、10 月 api 项目的账单合计多少元？
