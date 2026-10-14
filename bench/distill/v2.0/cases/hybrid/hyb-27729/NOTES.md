# hyb-7729 NOTES

- 会话形状：寒暄后派活（第 1 轮纯寒暄零调用，第 2 轮普通工具题）。
- 语言：英文。第 1 轮判据为零调用 + 应答词表；第 2 轮数值判（答案 7）。

## Traps

- 本题为 L0 基题，未埋陷阱。第 1 轮的约束（闲聊轮不调工具）写在判据里，不在 fixture 里。

## Reference solution

1. 第 1 轮：用户只是寒暄，直接回应问候即可，不调用任何工具（判据要求零调用且回复含应答词）。
2. 第 2 轮：读取 orders/june_orders.csv（全程第 1 次工具调用；题面已给路径）。
3. 统计 occasion 为 wedding 且日期在 2026-06 的行：7 张订单（ref_calls = 1）。

## Why the answer is unique

occasion 列只有 wedding、event、subscription 三种取值。README 写明一行一张订单，所以「多少张订单」就是「多少行」。把 event（2 行）或 subscription（1 行）算进来得到 9 或 8，与 wedding 不符；按 arrangements 求和得到的是花艺件数（任何一种口径都不是 7），与「多少张订单」不符。答案只有 7。

## Five alternative phrasings

1. Count the wedding orders in orders/june_orders.csv and give me the number alone.
2. How many June orders did we book for weddings? Data is at orders/june_orders.csv.
3. Look at the June order book and tell me the wedding order count, final figure only.
4. orders/june_orders.csv - how many rows are wedding orders?
5. Give me the June wedding order count from orders/june_orders.csv.
