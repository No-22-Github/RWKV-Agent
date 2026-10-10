## Traps
- TR-NEARNAME（恢复题，恢复行为是考点）: 题面要「实际成交额最高」的产地，表里没有叫「采购额」或「实付」的列，只有一对近名列：报价（下单时的报价金额）与成交额（对账后最终入账）。第一次对猜测的列做 group_by 求和会收到 `field "..." is missing` 或 `group_by field ... is missing` 报错；filter 引用不存在的列则返回 matched_rows 0。模型要从报错或空结果恢复：用不带 operation 的 data_query select 列出真实表头（或用题目预算内最多一次 read_file 看表头），再改用成交额重查。README 写明成交额才是最终入账金额。
- 按报价排名会推出 埃塞俄比亚 的 6519.58；正确答案是 云南保山 的成交额合计 5532.83。

## Reference solution
1. 读 README.md：成交额是最终入账的采购金额，报价只是下单时的报价。
2. data_query: {"path":"data/bean_purchases.csv","filter":{"采购月份":"2026-08"},"group_by":"产地","operation":"sum","field":"成交额"} -> 四个组合计，最高的是 云南保山 的 5532.83。（若第一次猜错列名报错：先发一次不带 operation 的 select 看到全部列名，再按本步重查。）
3. 终答只报数字 5532.83。

## Why the answer is unique
decoy 6519.58 按「报价」口径排名，但题面问实际成交额，README 写明成交额才是最终入账金额，两列每一行都不相等，按报价作答不成立。7 月与 9 月的行被月份条件排除。答案只有 5532.83。
