## Traps
- TR-DECOY: 巡检标记之前已有 tj-01 的「温控超限」ERROR，标记之后 tj-02 又有一条「温控超限趋势」WARN。按时间顺序第一条来自标记之前的记录属于巡检前，WARN 的级别也不是 ERROR，所以标记后第一条「温控超限」ERROR 来自 tj-03。

## Reference solution
1. 读 README.md：行格式、三个 ERROR 类别、标记行不算记录。
2. 看日志头部并检索「巡检窗口开始」标记，确认唯一。
3. 按顺序走标记之后的 ERROR 行，跳过其他类别的 ERROR 与温控超限 WARN。
4. 标记后第一条「温控超限」ERROR 的终端号是 tj-03。

## Why the answer is unique
标记行全库唯一，所以「巡检开始之后」有明确起点；标记前的温控超限 ERROR 在窗口之外，温控超限趋势是 WARN 不是 ERROR，其余两类 ERROR 的描述开头不同。答案是 tj-03。
