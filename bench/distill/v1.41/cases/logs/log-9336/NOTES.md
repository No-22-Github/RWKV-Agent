## Traps
- TR-DECOY: exact answer 97; the loose reading (区域和结果都用前缀匹配) gives 228.
- TR-TRUNC: the file is 72KB and 1341 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F';' '$3=="机房" && $4=="拒绝" {print $2}' 门禁/刷卡.txt | sort -u | wc -l` -> 97
Final answer: 机房拒绝涉及 97 张不同的卡。

## Why the answer is unique
区域 and 结果 are whole-value columns; cards are de-duplicated. The README (门禁/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 机房门禁拒绝过的不同卡号共有多少？
2. 区域是机房、结果是拒绝的记录，去重后有多少张卡？
3. 按说明.md，有多少张卡在机房被拒绝过？
4. 刷卡记录里被机房拒绝的卡号个数（去重）。
5. 统计机房拒绝记录涉及的不同卡号数量。
