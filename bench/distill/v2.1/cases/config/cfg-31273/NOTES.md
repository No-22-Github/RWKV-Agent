## Traps
- TR-ABSENT: 问题的后半部分（password_ttl）查不到。
- TR-DECOY: prod 的 90d 是别的环境。

## Reference solution
测试 host 能查到；password_ttl 只有 prod 有（90d）。

## Why the answer is unique
读 test.conf：host 10.20.0.31；没有 password_ttl。
