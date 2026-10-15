## Traps
修复装配质检汇总中把返工和拒收批次算入合格数的问题。
- TR-DECOY：inspection.csv 有 A16 rejected 900 和 C08 rework 600 两条较大干扰量；错误汇总会给出 A16=913、C08=612。

## Reference solution
1. 读取说明、数据和脚本，确定 accepted 的计入口径以及 CSV 输出契约。
2. 修正脚本，只累加 accepted 记录。
3. 运行脚本确认 stdout。共 3 次调用（读取可一次批量完成）。

## Why the answer is unique
A16 的 9+4=13，B04 的 5+7=12，C08 的 12=12；被拒收和返工批次均不属于合格件。README 指定字段名、升序、逗号分隔与无空格，因此唯一 stdout 为：
```
station,accepted_units
A16,13
B04,12
C08,12
```
只按运行行为判分，脚本源文件不设 equals。输入文件 unchanged 防止通过篡改数据凑出正确输出。

## Scoring boundary
自审应以两份不同源码（显式循环、筛选后分组）运行；CRLF 与末尾无换行也应通过。原始脚本、只排除 rejected 却保留 rework、只统计 accepted 行数均应失败。当前单输入运行无法排除把整个报表写死在脚本中的投机解；不声称验证所有未来输入。

## Primary review revision

按出题手册“一个陷阱且涉及至少3个文件”的较高难度规则，将L1校正为L2；现有lint同时允许L1/L2，不能只依赖lint给出一致分层。只改标签，不改任务内容或通过条件。

EXAM-CANARY-5e82a4c7
