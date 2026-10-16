## Traps
- TR-ABSENT: num.partitions 在被问的范围内没有定义。
- TR-DECOY: prod 配了 num.partitions=12，test 没有。

## Reference solution
读 server.test.properties：没有 num.partitions。

## Why the answer is unique
server.test.properties 里没有 num.partitions（只有 retention、segment 配置）；12 是 prod 的值。
