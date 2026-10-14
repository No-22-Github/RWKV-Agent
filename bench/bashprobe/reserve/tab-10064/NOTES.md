## Traps
- Answer: 408.
- TR-MULTISRC: 6 files; the first one alone gives 67.
- Data volume: 6 data files, 81 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 体检/2026/*.csv | awk -F, '$4=="是" {print $1}' | sort -u | wc -l` -> 408
Final answer: 有 408 位员工至少一项异常。

## Why the answer is unique
项目和异常是精确字段；说明写明复测不算。
