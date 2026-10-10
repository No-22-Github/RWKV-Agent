## Traps
- TR-DECOY: v4.0 的 3 次正是现值；v4.2 的 200 毫秒是另一个常量。

## Reference solution
1. 读依据 CHANGELOG.md，取出新值 5。
2. 读 pkg/client/defaults.go：要改的是第 4 行「MaxRetries    = 3 //」。
3. replace_lines 第 4 行为「MaxRetries    = 5 //」（同行其余内容和格式不动）。
4. 回读 pkg/client/defaults.go 确认。
终答示例：pkg/client/defaults.go 的 MaxRetries 已从 3 改为 5，依据是 CHANGELOG 的 v4.2 条目。
判据：目标文件逐字节等于预期。

## Why the answer is unique
依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。
