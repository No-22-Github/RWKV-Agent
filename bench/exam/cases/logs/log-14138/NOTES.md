## Traps
- TR-DECOY: INFO/WARN 行也含服务名；只数 ERROR。四个服务的 ERROR 数互不相同({'订单': 4, '支付': 1, '搜索': 3, '推送': 2})。
- 格式: 回答必须含 Markdown 表格(表头行 + |---| 分隔行)。

## Reference solution
1. 读/统计日志；2. 输出 Markdown 表格。

## Why the answer is unique
每个服务的 ERROR 条数唯一；四个数字都要出现在回答里。

EXAM-CANARY-d51fa10e
