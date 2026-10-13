## Traps
- TR-DECOY: globbing '*.xlsx' (lock files counted) gives 142; the README's rule gives 104.
- 170 files in nested folders under 报表/, so counting by listing is not practical.

## Reference solution
1. bash: `find 报表 -type f -name '*.xlsx' ! -name '~$*' | wc -l` -> 104
Final answer: 正式报表 104 份（~$ 锁文件和 .xls 不算）。

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
