## Traps
- TR-DECOY: 数字最像的 318.40/240.00 看起来大；最大是 512.75(R-2040, Marlow & Finch)。客户名含 & 符号。
- 子任务: 找最大、按给定句式追加一行、回答客户。

## Reference solution
1. 读 refunds.csv；2. 追加 `Largest refund: R-2040 512.75`；3. 回答 Marlow & Finch。

## Why the answer is unique
金额 512.75 为最大；文件行内容被钉住。

## Five alternative phrasings of the task
- Find the biggest refund in data/refunds.csv and add a line to the end of notes/summary.md that says 'Largest refund: <refund id> <amount>'. Then tell me which customer it was.
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-dcc78a76
