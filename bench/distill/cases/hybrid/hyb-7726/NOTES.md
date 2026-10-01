# hyb-7726 NOTES

- 会话形状：寒暄后派活（第 1 轮纯寒暄零调用，第 2 轮普通工具题）。
- 语言：中文。第 1 轮判据为零调用 + 应答词表；第 2 轮按数值判（答案 5）。

## Traps

- 本题为 L0 基题，未埋陷阱。第 1 轮的约束（闲聊轮不调工具）写在判据里，不在 fixture 里。

## Reference solution

1. 第 1 轮：用户只是寒暄，直接回应问候即可，不调用任何工具（判据要求零调用且回复含应答词）。
2. 第 2 轮：读取 exports/august_orders.csv（全程第 1 次工具调用；题面已给路径，无需先列目录）。
3. 逐行看 channel 列，取值为「直营」且日期在 2026-08 的行共 5 行，即 5 张订单（ref_calls = 1）。

## Why the answer is unique

channel 列只有三种取值：直营、批发、电商。README 写明一行对应一张订单、不存在重复行，所以「多少张订单」就是「多少行」。把批发（4 行）或电商（3 行）算进来得到的是 9 或 8，与「直营门店」这一定语不符；按 bags 列求和得到的是豆子袋数（任何一种口径都不是 5），与「多少张订单」不符。答案只有 5。

## Five alternative phrasings

1. 麻烦帮我数一下 8 月直营渠道的订单张数，明细在 exports/august_orders.csv。
2. exports/august_orders.csv 里 8 月发给直营门店的订单有几笔？只要数字。
3. 看下 8 月的订单导出，channel 是直营的有几行？报个数字就行。
4. 帮我统计 exports/august_orders.csv 中直营渠道的订单量，只回数字。
5. 8 月的订单明细在 exports/august_orders.csv，直营那部分一共几单？
