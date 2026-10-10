## Traps
- TR-DECOY: 容量规划表有 2025 和 2026 两列，2025 年的 24 正是配置里的现值；订单、通知的行也在表里。

## Reference solution
1. 读依据 容量规划.csv，取出新值 32。
2. 读 conf/pools.conf：要改的是第 3 行「库存.pool_size = 24」。
3. replace_lines 第 3 行为「库存.pool_size = 32」（同行其余内容和格式不动）。
4. 回读 conf/pools.conf 确认。
终答示例：conf/pools.conf 里库存服务的 pool_size 已从 24 改为 32，取自容量规划.csv 的 2026 年列。
判据：目标文件逐字节等于预期。

## Why the answer is unique
依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。
