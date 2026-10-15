## Traps
- 确认后磁盘上有 v2.4.0 和 ledgerline==2.4.0 两处；少改回一处失败。
- 日期必须是新值 2026-10-08，不是原来的 09-20。

## Reference solution
1. 第 1 轮：读，改两处版本。
2. 第 2 轮：读，改回两处并改日期。

## Why the answer is unique
整份文件内容被钉住：版本回到 2.3.0（两处），日期为 2026-10-08，其余原样。

## Five alternative phrasings of the task
- README.md 里的版本号从 v2.3.0 升到 v2.4.0，安装命令那行也一起改。
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-74c286b9
