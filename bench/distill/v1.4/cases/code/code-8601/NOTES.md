## Traps
- TR-DECOY: 未发布条目的 90 秒还在评审；2.5.0 的 30 秒正是现值。

## Reference solution
1. 读依据 CHANGELOG.md，取出新值 45。
2. 读 src/gateway.py：要改的是第 2 行「GATEWAY_TIMEOUT_S = 30」。
3. replace_lines 第 2 行为「GATEWAY_TIMEOUT_S = 45」（同行其余内容和格式不动）。
4. 回读 src/gateway.py 确认。
终答示例：src/gateway.py 的 GATEWAY_TIMEOUT_S 已按 CHANGELOG 2.6.0 的记录从 30 改为 45。 / DONE
判据：目标文件逐字节等于预期；终答含 DONE。

## Why the answer is unique
依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。
