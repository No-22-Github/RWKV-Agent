## Traps
无陷阱（L0 基题）：单条件计数。

## Reference solution
1. 读 README.md：每行一条预约，来源共三种。
2. 查询：{"path":"data/bookings_2026-07.csv","filter":{"来源":"老客推荐"},"operation":"count"}，得 4.0。
3. 终答只给数字 4.0。

## Why the answer is unique
计数口径是行数，过滤条件来源=老客推荐唯一确定行集合，答案唯一。
