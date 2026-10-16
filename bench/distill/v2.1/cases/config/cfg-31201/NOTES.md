## Traps
- TR-ABSENT: max_retry_backoff 在被问的范围内没有定义。
- TR-DECOY: staging.yaml 里有 max_retry_backoff: 3000，但被问的是 prod，prod 没有这个键。

## Reference solution
读 prod.yaml：没有 max_retry_backoff；staging 的 3000 属于另一环境。

## Why the answer is unique
答案：prod.yaml 里没有 max_retry_backoff（只有 retry_max=5、timeout_ms=1800），staging 的 3000 不能算 prod 的值，建议向负责人确认或显式补上。
