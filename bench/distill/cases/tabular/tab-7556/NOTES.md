## Traps
- TR-NEARNAME（恢复题，恢复行为是考点）: 题面只说「按对账口径的应收合计」，表里没有叫「对账金额」或「应收金额」的列，只有一对近名列：不含税金额（README 写明是对账与开票口径）与含税金额（仅供税额申报）。第一次用猜测的列名聚合会收到 `field "..." is missing` 报错；filter 引用不存在的列则返回 matched_rows 0。模型要从报错或空结果恢复：用不带 operation 的 data_query select 列出真实表头（或用预算内最多一次 read_file 看表头），再改用不含税金额重查。
- 顺手聚合含税金额会得到差额 8775.33；正确答案是不含税口径的差额 6643.99。

## Reference solution
1. 读 README.md：对账口径是不含税金额；银行流水按记账月份归属。
2. 查询一：{"path":"data/ledger_2026-09.csv","filter":{"月份":"2026-09"},"operation":"sum","field":"不含税金额"}，得 23681.84。（若第一次猜错列名报错：先 select 看全部列名，再按本步重查。）
3. 查询二：{"path":"data/bank_2026-09.csv","filter":{"记账月份":"2026-09"},"operation":"sum","field":"金额"}，得 17037.85。
4. 相减得 6643.99，终答只报数字。

## Why the answer is unique
decoy 8775.33 用了含税金额，但 README 写明含税金额仅供税额申报、对账按不含税；银行侧 8 月流水被月份条件排除。答案唯一为 6643.99。
