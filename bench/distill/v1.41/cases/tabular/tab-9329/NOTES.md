## Traps
- TR-DECOY: exact answer 133; the loose reading (整行包含B3，含B30和备注) gives 247.
- TR-MULTISRC: 4 files; the first file alone gives 32.

## Reference solution
Turn 1: bash: `cat 快递柜/*.txt | awk -F'\t' '$2=="B3"' | wc -l` -> 133
Final answer: B3 柜共有 133 条取件记录。

## Why the answer is unique
柜号 is a whole-value column; B3 elsewhere in the line does not count. The README (快递柜/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. B3 柜被取了多少次件？
2. 统计柜号列恰好等于 B3 的记录条数。
3. 按说明.md，四栋楼里 B3 柜的取件记录有几条？
4. 快递柜记录中柜号是 B3（不是 B30）的行数。
5. 四个文件合计，B3 柜的取件次数是多少？
