## Traps
- TR-DECOY: data/maintenance_log.csv 里 2026-08 共 28 行，修剪只有 8 行，其余 20 行是浇灌、施肥等作业，笔数更多、费用同量级。只按月份求平均得到 2660.2589，是把全部作业混在一起的错误答案；题面只要修剪作业，8 次平均 2768.8125 元。

## Reference solution
1. 用 data_query 聚合：{{"path":"data/maintenance_log.csv","filter":{{"作业类型":"修剪","作业月份":"2026-08"}},"operation":"avg","field":"作业费用"}}，得 2768.8125。
2. 终答只报数字 2768.8125。

## Why the answer is unique
decoy 2660.2589 来自把 8 月全部作业混进分母，但题面明确限定修剪作业，其他作业的行不属于本题。其他月份的行被作业月份条件排除。答案只有 2768.8125。
