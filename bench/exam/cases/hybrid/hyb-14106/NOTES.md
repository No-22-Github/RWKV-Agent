## Traps
- 拒绝后磁盘是原文件。模型若认为三条仍在，不会补加；若加了三条则多了第二条。
- 条目顺序：第一条在前，第三条在后，且紧接原文，无空行。

## Reference solution
1. 第 1 轮：读，追加三条。
2. 拒绝后：读（原文），追加第一、三条。

## Why the answer is unique
终态必须恰为原文加两行，第二条整理服务器清单不得出现（整段连续内容被钉住）。

## Five alternative phrasings of the task
- 在 本周待办.md 末尾加三条待办：1) 把监控告警阈值发给张莉确认；2) 整理上季度的服务器清单；3) 预订周五的评审会议室。
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-01f004ce
