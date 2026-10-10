## Traps
- TR-DECOY: logging-interceptor 同组且版本不同（4.11.0），读错行会写成 4.11.0。

## Reference solution
1. 读依据 gradle.lockfile，取出新值 4.12.0。
2. 读 build.gradle：要改的是第 2 行「okhttp:4.9.3'」。
3. replace_lines 第 2 行为「okhttp:4.12.0'」（同行其余内容和格式不动）。
4. 回读 build.gradle 确认。
终答示例：build.gradle 里 okhttp 已从 4.9.3 改为 4.12.0，与 gradle.lockfile 一致，logging-interceptor 没动。
判据：目标文件逐字节等于预期。

## Why the answer is unique
依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。
