## Traps
- TR-DECOY: exact answer 2818; the loose reading (班次前缀匹配，含早班(加班)) gives 3803.
- TR-TRUNC: the file is 85KB and 1242 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$4=="早班" {s[$2]+=$3} END{m=0; for (k in s) if (s[k]>m) m=s[k]; print m}' 产量/日报.dat` -> 2818
Final answer: 早班产量最高的工位合计 2818。

## Why the answer is unique
班次 is a whole-value column; the answer is the maximum of the per-station sums. The README (产量/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 各工位早班产量加起来，最大的合计数是多少？
2. 班次恰好是早班的产量按工位求和，取最大值。
3. 按说明.md，早班里产量最高工位的合计。
4. 早班(加班)不算，各工位合计的最大值是多少？
5. 汇总早班产量，哪个工位最多？告诉我那个合计数。
