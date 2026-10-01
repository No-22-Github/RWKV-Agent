## Traps
- 无陷阱（L0 基题）。状态表里 user.export 是灰度中、其余正常，注意行对应。

## Reference solution
1. 取题面给出的 https://open.banxia.example/status。
2. 找到 sms.send 行：已弃用（2026-07-15 起），短信改用 sms.batch，作答。

## Why the answer is unique
状态页按接口逐行列出，sms.send 一行只有「已弃用（2026-07-15 起）」一个状态；order.create、stock.sync 正常，user.export 灰度中，都不对应 sms.send。答案唯一。

## 正确答案
已弃用（2026-07-15 起），短信请改用 sms.batch

## Five alternative phrasings
1. 半夏收银 sms.send 状态
2. 半夏 开放平台 接口状态
3. 半夏 短信接口 sms.send
4. 半夏收银 短信 弃用
5. 半夏收银 状态页 接口
