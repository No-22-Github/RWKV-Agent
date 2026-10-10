## Traps
- TR-NEARNAME（恢复题，恢复行为是考点）: 题面问「多少位顾客」，表里没有叫「顾客」的列，只有一对近名列：客户编号（唯一标识一位顾客）与客户类别（散客、会员、企业三个客群）。第一次对猜测的列做 distinct_count 会收到 `field "..." is missing` 之类的报错；filter 引用不存在的列则返回 matched_rows 0。模型要从报错或空结果恢复：用不带 operation 的 data_query select 列出真实表头（或用题目预算内最多一次 read_file 看表头），再改用客户编号重查。README 写明客户编号才是「人」这一级。
- 按客户类别去重只会得到 3；正确答案是不同顾客的人数 24。

## Reference solution
1. 读 README.md：客户编号唯一标识一位顾客，客户类别是多位顾客共用的客群标签。
2. data_query: {"path":"data/pickup_records.csv","filter":{"收衣月份":"2026-09","服务类型":"羽绒服清理"},"operation":"distinct_count","field":"客户编号"} -> 24。（若第一次猜错列名报错：先发一次不带 operation 的 select 看到全部列名，再按本步重查。）
3. 终答只报数字 24。

## Why the answer is unique
decoy 3 数的是客群类别，但题面问多少位不同的顾客，README 写明多位顾客共用一个类别，类别数答不了人数。8 月的行与其他服务类型被过滤条件排除。答案只有 24。
