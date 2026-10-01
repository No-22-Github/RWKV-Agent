## Traps
- TR-RULEFILE: 合并规则的例外在 cities.yaml 的 floor_rule：差异费率低于 2.5 时按 2.5 保底。徐汇店差异费率 2.2，只看 stores.csv 直接报差异值会得到 2.2；套用保底后生效值是 2.5。

## Reference solution
1. 读 stores.csv：徐汇店，上海，差异费率 2.2。
2. 读 cities.yaml：门店差异优先，但低于 2.5 时按 2.5 保底。
3. 2.2 低于 2.5，生效值 2.5。

## Why the answer is unique
徐汇店的差异值 2.2 是唯一的表内读数，而 cities.yaml 的 floor_rule 明确写了保底口径，2.2 触发保底后只有 2.5 一个结果；把 2.2 当生效值的读法只完成了第一步合并、丢掉了同一条规则里的保底半句，与文件语义不符。答案唯一为 2.5。
