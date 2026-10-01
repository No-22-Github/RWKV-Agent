## Traps
- TR-DUPROW: 导出重试把 4 行整行重复写进文件，其中 East 的重复行会让按行计数得 52；README 写明 item_code 标识副本、重复行是同一件书。题面问多少种不同 item，按 item_code 去重后为 50。

## Reference solution
1. 读 README.md：item_code 标识副本，导出重试会产生整行重复。
2. 查询：{"path":"data/returns_2026-09.csv","filter":{"return_month":"2026-09","branch":"East"},"operation":"distinct_count","field":"item_code"}，得 50.0。
3. 终答只报数字 50.0。

## Why the answer is unique
decoy 52 把重复写出的行当成了不同的 item，与 README 写明的重试语义矛盾；重复行与原行逐列相同，没有任何读法能把它们当成不同副本。答案唯一为 50.0。
