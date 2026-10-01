## Traps
- TR-DUPROW: 采集器重发使 success 回调共 27 行，按回调号去重后是 22 个；按行加总会得 2214.55。
- TR-CLAIM: close 前的日终汇总草稿写 fee_total_cny 1882.02，README 写明它是草稿值不是事件记录；真值是 2188.40。

## Reference solution
1. 读 README.md：记录结构、日终汇总的定位、重发规则。
2. 检索 status=success，逐行读取 fee_cny。
3. 按回调号取首次出现，加总 fee_cny。
4. 合计 2188.40（保留两位小数）。

## Why the answer is unique
日终汇总不是事件记录，被 README 排除；重发行与原行逐字段相同，去重后不重复计费；timeout 状态不计入。答案是 2188.40。
