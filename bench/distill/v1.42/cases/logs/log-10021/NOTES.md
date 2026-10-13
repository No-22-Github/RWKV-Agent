## Traps
- Answer: 南门.
- TR-MULTISRC: 10 files; the first one alone gives 北门.
- Data volume: 10 data files, 153 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 门禁/记录/*.log | grep ' 结果=拒绝 ' | awk '{print $2}' | sort | uniq -c | sort -rn | head -3` -> 南门
Final answer: 拒绝最多的是 南门。

## Why the answer is unique
门和结果都是精确字段；北门辅道按说明单独算。
