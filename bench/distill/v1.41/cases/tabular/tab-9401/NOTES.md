## Traps
- TR-DECOY: exact answer 2517; the loose reading (药品、状态前缀匹配) gives 4737.
- TR-MULTISRC: 4 files; the first file alone gives 464.

## Reference solution
Turn 1: bash: `cat 药房出库/*.txt | awk -F'\t' '$2=="布洛芬" && $3=="已发" {s+=$4} END{print s}'` -> 2517
Final answer: 2517 盒。

## Why the answer is unique
药品 and 状态 are whole-value columns. The README (药房出库/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 布洛芬（不含缓释）已发的盒数合计是多少？
2. 把四周里布洛芬、已发的数量加起来。
3. 按说明.md，布洛芬已发出库共多少盒？
4. 药品列等于布洛芬且状态列等于已发的数量总和。
5. 统计布洛芬正式出库（不含补录）的总盒数。
