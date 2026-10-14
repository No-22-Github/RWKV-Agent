## Traps
- Answer: 98. TR-DECOY: counting 北门辅道 too gives 135.
- TR-MULTISRC: 10 files; the first one alone gives 9.
- Data volume: 10 data files, 154 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 门禁/记录/*.log | grep ' 门=北门 ' | grep -c ' 结果=拒绝 '` -> 98
Final answer: 北门共拒绝 98 次（北门辅道不算）。

## Why the answer is unique
门和结果都是精确字段；北门辅道按说明单独算。
