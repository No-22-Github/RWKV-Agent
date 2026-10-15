## Traps
- 第 1 轮改的两处暂存改动在第 2 轮前被用户全部拒绝，磁盘上仍是原文件。若模型以为 staging 已经是 60 而不再动手，终态 staging 仍是 30，失败。
- 若模型以为 prod 也被改成 60 而去“改回 30”，结果相同，不扣分；若模型把 prod 也改成 60，失败。
- 判分只看终态文件；第 1 轮是过渡轮，expect 为空。

## Reference solution
1. 第 1 轮：读 conf/services.ini，把两处 request_timeout 改 60（暂存，2–3 步）。
2. 用户拒绝后：重新读文件（原样），只改 [staging] 的 request_timeout = 60（2 步）。
终态：[prod] 段 request_timeout = 30，[staging] 段 request_timeout = 60，其余原样。

## Why the answer is unique
用户明确说只改 staging、prod 保持原样，两段其余内容也要求不变；判分钉住整份文件内容，prod 或 staging 任一不符都不过。

## Five alternative phrasings of the task
- 把 conf/services.ini 里 prod 和 staging 的 request_timeout 都改成 60 吧。
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-a3c3217f
