## Traps
- Answer: 8.
- Data volume: 1 data files, 101 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The answer sits in the last part of the file; a read that stops at 64KB sees an earlier match or none.

## Reference solution
1. bash: `grep '时间=2026-09' 发布/发布记录.log | grep -c ' 结果=回滚$'` -> 8
Final answer: 九月回滚 8 次。

## Why the answer is unique
记录按时间顺序追加，最后一条匹配行就是最近一次。
