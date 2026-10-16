## Traps
- TR-ABSENT: 问题的后半部分（memory_limit）查不到。
- TR-DECOY: dev 文件里有近似的 memory_limit。

## Reference solution
replicas=6 能查到；memory_limit 只在 dev 里有（512Mi），prod 没有。

## Why the answer is unique
读 prod 文件：replicas 6；没有 memory_limit，dev 的 512Mi 不能算。
