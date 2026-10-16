## Traps
- TR-ABSENT: new_checkout 在被问的范围内没有定义。
- TR-DECOY: prod.json 里 new_checkout 是 true，test.json 里根本没有这个开关。

## Reference solution
读 test.json：没有 new_checkout。

## Why the answer is unique
test.json 里没有 new_checkout 这个开关（只有 dark_mode、new_search），不能说开或关；prod.json 的 true 不代表测试环境。
