## Traps
- TR-DECOY: 近名课 Wheel Taster Week 在 9 月开了 28.0 次，与 Wheel Taster 并排出现；两者是不同的课，精确相等过滤下 Wheel Taster 不匹配 Wheel Taster Week，按 Week 作答不成立。

## Reference solution
1. 查询：{"path":"data/sessions_2026-09.csv","filter":{"session_month":"2026-09","session":"Wheel Taster"},"operation":"count"}，得 14.0。
2. 终答只报数字 14.0。

## Why the answer is unique
一行对应一节已预订的课（README），数行数即数课次；近名课与月份外的行都被精确相等过滤排除。答案唯一为 14.0。
