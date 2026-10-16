## Traps
- TR-ABSENT: 问题的后半部分（不同 IP）查不到。
- TR-DECOY: 用户名不是 IP。

## Reference solution
失败 3 次能数出来；日志没有记录 IP。

## Why the answer is unique
读日志：失败 3 行；日志里没有 IP 字段，所以数不出来。
