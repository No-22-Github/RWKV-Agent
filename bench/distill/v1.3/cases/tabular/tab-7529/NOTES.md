## Traps
- TR-SIGN: 退货与折价以正数记账。把它们当成额外收入加进销售合计会得到 9711.11；README 写明净销售额要把退货与折价从销售合计中扣掉。
- TR-MULTISRC: 只看销售明细得到 7521.76，是毛额。退货记录在另一份台账里，只看一份对不出净额。

## Reference solution
1. 读 README.md：退货与折价以正数记账，净销售额 = 销售合计扣除退货与折价。
2. data_query: {"path":"data/sales_ledger.csv","filter":{"结算月份":"2026-08"},"operation":"sum","field":"金额"} -> 7521.76。
3. data_query: {"path":"data/credits_ledger.csv","filter":{"结算月份":"2026-08"},"operation":"sum","field":"金额"} -> 2189.35。
4. 相减：7521.76 - 2189.35 = 5332.41。
5. 终答只报数字 5332.41。

## Why the answer is unique
decoy 9711.11 把正数记账的退货当成收入，与 README 的记账语义矛盾；decoy 7521.76 是毛额，而题面问的是扣完退货与折价的净额，定义上需要两份台账。7 月与 9 月的行被月份条件排除。答案只有 5332.41。
