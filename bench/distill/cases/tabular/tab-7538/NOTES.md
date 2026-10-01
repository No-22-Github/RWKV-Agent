## Traps
- TR-HEADER: 末行是系统生成的当月合计（genre 为 ALL，README 写明不是一笔销售），对金额列整列求和会把合计行算进去，得 9486.64。
- TR-DECOY: 近名流派 Jazz Fusion 在 9 月的合计为 1907.99，比 Jazz 更大更醒目；两者是不同流派，精确相等过滤下 Jazz 不匹配 Jazz Fusion，按 Fusion 作答不成立。

## Reference solution
1. 读 README.md：末行是系统合计，不是销售。
2. 查询：{"path":"data/vinyl_sales_2026-09.csv","filter":{"sale_month":"2026-09","genre":"Jazz"},"operation":"sum","field":"amount_gbp"}，得 581.35。
3. 终答只报数字 581.35。

## Why the answer is unique
decoy 9486.64 把非销售的合计行当成了销量；decoy 1907.99 把另一个流派的销售额当成了 Jazz 的。两者都与 README 的字段语义或流派名矛盾。Jazz 行被精确相等过滤唯一确定，答案唯一为 581.35。
