## Traps
- TR-ABSENT: spool_dir 在被问的范围内没有定义。
- TR-DECOY: dev 配了 spool_dir=/tmp/pq-spool；生产只有 log_dir。

## Reference solution
读 queue.prod.conf：没有 spool_dir。

## Why the answer is unique
queue.prod.conf 没有 spool_dir（只有 log_dir=/var/log/pq），/tmp/pq-spool 是 dev 的值，不能给生产。
