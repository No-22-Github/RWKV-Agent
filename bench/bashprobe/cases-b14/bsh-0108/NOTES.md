## Traps
- Answer: 104. TR-DECOY: counting 血压复测 gives 235.
- TR-MULTISRC: 6 files; the first one alone gives 16.
- Data volume: 6 data files, 78 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 体检/2026/*.csv | awk -F, '$2=="血压" && $4=="是"' | wc -l` -> 104
Final answer: 血压异常 104 条（不含血压复测）。

## Why the answer is unique
项目和异常是精确字段；说明写明复测不算。
