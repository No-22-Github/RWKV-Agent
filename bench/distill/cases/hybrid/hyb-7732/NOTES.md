# hyb-7732 NOTES

- 会话形状：派活后道谢再追问（第 1 轮求和任务，第 2 轮道谢 + 追问最大单笔）。
- 语言：中文。两轮都按数值判：第 1 轮答案 1284.50，第 2 轮答案 356.50。

## Traps

- 本题为 L0 基题，未埋陷阱。

## Reference solution

1. 第 1 轮：读取 finance/butter_september.csv（第 1 次工具调用）。
2. 对金额列求和：218.00 + 356.50 + 189.00 + 341.00 + 180.00 = 1284.50。
3. 第 2 轮：取金额列最大值 356.50（第 2 次工具调用，重读同一文件；ref_calls = 2）。

## Why the answer is unique

1284.50 是金额列的完整求和；漏掉任何一行（比如漏掉 180.00 得 1104.50）或只算某个供应商（青禾商贸 536.50）都不等于全部支出。356.50 是金额列唯一的最大值，其余四笔分别小于它；按日期取第一笔（218.00）或把供应商名当金额读都得不到它。答案分别只有 1284.50 和 356.50。

## Five alternative phrasings

1. 把 finance/butter_september.csv 里 9 月的黄油采购金额加一下，只要总数。
2. 9 月黄油流水合计是多少？文件在 finance/butter_september.csv。
3. 帮我汇总 finance/butter_september.csv 的采购支出，只回数字。
4. 这份黄油采购流水总共花了多少钱？
5. 统计 9 月黄油采购总金额，明细在 finance/butter_september.csv。
