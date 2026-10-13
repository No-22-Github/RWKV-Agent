## Traps
- Answer: 323.
- TR-MULTISRC: 5 files; the first one alone gives 62.
- Data volume: 5 data files, 37 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no perl, so running 统计/退货.pl fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat 客服记录/*.txt | grep '^顾客：' | grep -c 退货` -> 323
Final answer: 退货.pl 会输出 323（只算顾客说的、含「退货」的行）。

## Why the answer is unique
脚本统计以「顾客：」开头且包含「退货」的行。
