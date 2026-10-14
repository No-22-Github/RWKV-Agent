## Traps
- Answer: 运营部.
- Data volume: 6 data files, 80 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 体检/2026/*.csv | awk -F, '$2=="视力" && $4=="是" {print $5}' | sort | uniq -c | sort -rn | head -3` -> 运营部
Final answer: 视力异常最多的是 运营部。

## Why the answer is unique
项目和异常是精确字段；说明写明复测不算。
