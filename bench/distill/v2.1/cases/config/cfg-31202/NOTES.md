## Traps
- TR-ABSENT: db_pool_size 在被问的范围内没有定义。
- TR-DECOY: dev.yaml 里有 db_pool_size: 4；prod 只有近名键 db_pool_min: 8。

## Reference solution
读 base 与 prod：都没有 db_pool_size；prod 只有 db_pool_min=8，不是同一个键。

## Why the answer is unique
prod.yaml 与 base.yaml 都没有 db_pool_size，只有 db_pool_min: 8（最小连接数，不等于池大小）；dev 的 4 不适用。
