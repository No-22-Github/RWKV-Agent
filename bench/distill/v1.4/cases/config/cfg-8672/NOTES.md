## Traps
- TR-DECOY: serde_json 的 1.0.128 与 serde 同前缀，读错块会写成 1.0.128。

## Reference solution
1. 读依据 Cargo.lock，取出新值 1.0.210。
2. 读 Cargo.toml：要改的是第 6 行「serde = "1.0.190"」。
3. replace_lines 第 6 行为「serde = "1.0.210"」（同行其余内容和格式不动）。
4. 回读 Cargo.toml 确认。
终答示例：Cargo.toml 的 serde 已从 1.0.190 改为 1.0.210，与 Cargo.lock 一致；serde_json 没动。
判据：目标文件逐字节等于预期。

## Why the answer is unique
依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。
