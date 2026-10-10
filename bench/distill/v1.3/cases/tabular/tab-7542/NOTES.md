## Traps
- TR-DECOY: 近名团 Sunset Tour Plus 在 9 月的预订单数为 33.0，比 Sunset Tour 更大更醒目；两者是不同的团，精确相等过滤下 Sunset Tour 不匹配 Sunset Tour Plus，按 Plus 作答不成立。

## Reference solution
1. 查询：{"path":"data/bookings_2026-09.csv","filter":{"booking_month":"2026-09","tour":"Sunset Tour"},"operation":"count"}，得 12.0。
2. 终答只报数字 12.0。

## Why the answer is unique
一行对应一张预订单（README），数行数即数订单；近名团与月份外的行都被精确相等过滤排除。答案唯一为 12.0。
