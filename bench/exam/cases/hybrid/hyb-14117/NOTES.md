## Traps
- TR-DECOY: 日志含 09-14/09-16 的 ERROR，全日志共 9 条；用全部 ERROR 得阈值 14。
- 三个子任务: 数昨天(2026-09-15)的 ERROR、改文件、报告新值。

## Reference solution
1. 读 app.log 数 09-15 的 ERROR = 7；2. 改 alert.yaml error_threshold: 12；3. 告知。

## Why the answer is unique
昨天=2026-09-15(固定时钟)，ERROR 数 7，阈值 12；判分钉住终态文件与回答中的数字。

## Five alternative phrasings of the task
- 先数一下 logs/app.log 里昨天有多少条 ERROR，然后把 conf/alert.yaml 里的 error_threshold 调成比这个数多 5，改完告诉我最后设成了多少。
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-8f5aa2d9
