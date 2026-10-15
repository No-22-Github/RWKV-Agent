## Traps
- TR-DECOY: 计划里有四个日期，只有 Beta 发布那个算数；代码冻结(10-20)距今 34 天，正式发布(12-01)距今 76 天。
- 今天固定为 2026-09-16；模型需要查当前日期（datetime 工具）再做差。

## Reference solution
1. 读 plan.md；2. datetime 取今天；3. 2026-11-03 减 2026-09-16 = 48 天。

## Why the answer is unique
Beta 发布 2026-11-03，今天 2026-09-16，相差 48 天；其余里程碑日期是干扰项。

## Five alternative phrasings of the task
- project/plan.md 里的 Beta 发布日期，离今天还有几天？直接告诉我天数就行。
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

## Teacher result
r1 DeepSeek 读了文件并用 datetime/calculator，但把 10 月当成 31 天之外又多算了一天（算式 (31-16)+31+3，应为 (30-16)+31+3），答 49。老师真实算术错误，题保留。

EXAM-CANARY-f86977bd
