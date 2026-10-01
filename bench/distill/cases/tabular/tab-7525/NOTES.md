## Traps
- TR-DUPROW: 导出里有四条目标预约被重试重复写入，按行数数会得到 28。README 写明预约号唯一标识一条预约，所以答案应当是不同会员的人数 22。

## Reference solution
1. 读 README.md：重试会把同一条预约重复写入；会员号唯一标识一位会员。
2. data_query: {"path":"data/seat_bookings.csv","filter":{"预约月份":"2026-09","时段":"晚间"},"operation":"distinct_count","field":"会员号"} -> 22。
3. 终答只报数字 22。

## Why the answer is unique
decoy 28 数的是行数，但题面问的是多少位不同的会员，README 写明重试会重复写入同一条预约，重复行与原行逐列相同，不存在把它们当成不同会员的读法。8 月的行被月份条件排除。答案只有 22。
