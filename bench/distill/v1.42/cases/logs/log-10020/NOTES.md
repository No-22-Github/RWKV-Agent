## Traps
- Answer: 157.
- TR-MULTISRC: 10 files; the first one alone gives 17.
- Data volume: 10 data files, 154 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 门禁/记录/*.log | grep ' 结果=超时 ' | awk '{print $3}' | sort -u | wc -l` -> 157
Final answer: 共有 157 张不同的卡出现过超时。

## Why the answer is unique
门和结果都是精确字段；北门辅道按说明单独算。
