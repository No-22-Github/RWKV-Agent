## Traps
- TR-DUPROW: 导出重试把 4 行整行重复写入，其中 Tune-Up 的重复行让按行计数得 39；README 写明 customer_code 标识客户、重复行是同一工单被写了多次。
- TR-DECOY: 近名服务 Tune-Up Plus 的不同客户数为 27，与 Tune-Up 并排出现；两者是不同的服务项目，精确相等过滤下 Tune-Up 不匹配 Tune-Up Plus。

## Reference solution
1. 读 README.md：导出重试会产生整行重复，客户按 customer_code 计。
2. 查询：{"path":"data/jobs_2026-09.csv","filter":{"job_month":"2026-09","service":"Tune-Up"},"operation":"distinct_count","field":"customer_code"}，得 37.0。
3. 终答只报数字 37.0。

## Why the answer is unique
decoy 39 把重复写出的行当成了不同客户，与 README 矛盾；decoy 27 数的是另一项服务的客户。去重后的客户集合被精确相等过滤唯一确定，答案唯一为 37.0。
