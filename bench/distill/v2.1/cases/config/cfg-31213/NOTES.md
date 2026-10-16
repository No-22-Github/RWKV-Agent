## Traps
- TR-ABSENT: receipt_copies 在被问的范围内没有定义。
- TR-DECOY: 上海店 receipt_copies=2；杭州店与 defaults.json 都没有该键。

## Reference solution
读 store_hz.json 与 defaults.json：都没有 receipt_copies。

## Why the answer is unique
杭州店 store_hz.json 和 defaults.json 都没有 receipt_copies；上海店的 2 份不能套用。
