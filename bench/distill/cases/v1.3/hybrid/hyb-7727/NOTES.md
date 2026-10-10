# hyb-7727 NOTES

- 会话形状：派活后道谢再追问（第 1 轮订单数任务，第 2 轮道谢 + 追问总袋数）。
- 语言：英文。两轮都按数值判：第 1 轮答案 7，第 2 轮答案 22。

## Traps

- TR-DUPROW: exports/march_orders.csv 里 BL-3402、BL-3411（批发）和 BL-3418（零售）各写了两行，README 说明导出任务重试过。不注意会得到：按行数回答批发订单数得 9（7 张订单 + 2 张重复行），trap_decoys 记 9；第 2 轮按行累加袋数得 32 而不是 22。

## Reference solution

1. 第 1 轮：读取 exports/march_orders.csv，README 说明一行一个订单行且导出会重复写（第 1 次工具调用）。
2. 取 channel 为 wholesale 且日期在 2026-03 的行，按 order_id 去重：BL-3402、BL-3411、BL-3421、BL-3430、BL-3434、BL-3438、BL-3441，共 7 张订单。
3. 第 2 轮：对同一批 7 张订单的 bags 求和：4+6+2+1+4+2+3 = 22 袋（第 2 次工具调用；ref_calls = 2）。

## Why the answer is unique

9 来自把重复行当成不同订单，但 README 写明导出任务重试、每张订单可能写多行，且重复行与原始行逐列完全相同，没有任何一种读法能把它们算成两张订单，所以订单数只看不同 order_id，是 7。32 来自把重复行的袋数也累加，同理这些行是同一次出货的重复记录，只计一次，总数是 22。把订阅（BL-3406、BL-3426）或零售（BL-3414、BL-3418）的行算进来会得到 9 到 11 张订单，与「wholesale cafes」这一筛选不符。

## Five alternative phrasings

1. Count the wholesale cafe orders we shipped in March 2026; the export is at exports/march_orders.csv.
2. exports/march_orders.csv - how many orders went to the wholesale channel in March?
3. Look at the March export and tell me the number of wholesale orders, final figure only.
4. How many separate wholesale orders left us in March 2026? Data is in exports/march_orders.csv.
5. Give me the March 2026 wholesale order count from exports/march_orders.csv.
