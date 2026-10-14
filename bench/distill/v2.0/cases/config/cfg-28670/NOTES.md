## Traps
- TR-DECOY: 锁文件里 dayjs-plugin-utc 的 0.9.2 紧跟在 dayjs 后面；lodash 已一致。

## Reference solution
1. 读依据 package-lock.json，取出新值 1.11.13。
2. 读 package.json：要改的是第 4 行「"dayjs": "1.10.7"」。
3. replace_lines 第 4 行为「"dayjs": "1.11.13"」（同行其余内容和格式不动）。
4. 回读 package.json 确认。
终答示例：package.json 里 dayjs 已从 1.10.7 改为 1.11.13，与 package-lock.json 一致。
判据：目标文件逐字节等于预期。

## Why the answer is unique
依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。
