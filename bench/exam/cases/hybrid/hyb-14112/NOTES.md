## Traps
- 浮点表示 1.2676506002282294e+30 不是精确值；2**100 必须写满 31 位。

## Reference solution
1. 读 culture.md(起始 1，每天翻倍，100 天)；2. 精确计算 2^100 = 1267650600228229401496703205376。

## Why the answer is unique
每天翻倍、第 100 天结束 = 2^100，精确整数唯一。千分位写法也接受。

## Five alternative phrasings of the task
- Following the plan in lab/culture.md, how many cells will there be at the end of day 100? I need the exact figure, every digit.
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-d343219e
