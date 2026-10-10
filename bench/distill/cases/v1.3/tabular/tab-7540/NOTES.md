## Traps
- TR-DUPROW: 导出重试把 4 行整行重复写入，其中 Auto-Refill 的重复行让按行计数得 36；README 写明 patient_code 标识患者、重复行是同一笔配药被写了多次。题面问多少位不同患者，按 patient_code 去重后为 33。

## Reference solution
1. 读 README.md：导出重试会产生整行重复，患者按 patient_code 计。
2. 查询：{"path":"data/refills_2026-09.csv","filter":{"refill_month":"2026-09","channel":"Auto-Refill"},"operation":"distinct_count","field":"patient_code"}，得 33.0。
3. 终答只报数字 33.0。

## Why the answer is unique
decoy 36 把重复写出的行当成了不同患者；重复行与原行逐列相同，没有读法能把它们算成不同的人。答案唯一为 33.0。
