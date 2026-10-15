## Traps
- 用户确认后磁盘上是 200；“原来的值”是 20，只在第 1 轮对话/读文件结果里出现过。若模型随便写个别的值（如 100、50）失败。
- 判分只看终态文件，必须等于原文。

## Reference solution
1. 第 1 轮：读文件，改 max_upload_mb: 200。
2. 第 2 轮：读文件（已是 200），改回 20（2 步）。

## Why the answer is unique
“改回原来的值”只有 20 一种读法；终态整份文件与原文一致。

## Five alternative phrasings of the task
- 把 conf/limits.yaml 里的 max_upload_mb 改成 200，客户要传大文件。
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-3da77933
