## Traps
- TR-DECOY: 忽略节假日只跳周末得到 2026-10-07；把 15 个日历日当工作日得到 2026-10-01。
- 从明天(09-17)开始数第 1 个工作日，不含今天。

## Reference solution
1. 读 closures.txt；2. 取今天 2026-09-16(周三)；3. 逐日跳过周末与关门日，数到第 15 个 = 2026-10-14。

## Why the answer is unique
起算日规则在题面中给出(不含今天)，关门日列表在文件里；第 15 个工作日是 2026-10-14。

## Five alternative phrasings of the task
- We freeze the schedule 15 working days from today, not counting today. Weekends are off and so are the closure days in calendar/closures.txt. What date does the freeze land on?
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-57bc9619
