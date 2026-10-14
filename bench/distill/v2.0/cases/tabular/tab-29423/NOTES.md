## Traps
- TR-DECOY: exact answer 29; the loose reading (渠道和状态都前缀匹配) gives 8.
- TR-TRUNC: the file is 80KB and 1200 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="微信" && $3=="失败" {print NR; exit}' 交易/交易.tsv` -> 29
Final answer: 第一条微信失败记录在第 29 行。

## Why the answer is unique
渠道 and 状态 are whole-value columns; the header counts as line 1. The README (交易/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 交易流水里微信渠道第一次失败发生在第几行？
2. 渠道是微信、状态是失败的记录，最靠前的一条行号是多少？
3. 按说明.md，微信失败的首条记录位于哪一行（表头算第 1 行）？
4. 微信小程序不算，微信渠道第一笔失败的行号。
5. 找到第一条微信失败的交易，告诉我它在文件的第几行。
