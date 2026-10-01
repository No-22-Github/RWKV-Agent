## Traps
- 无陷阱（L0 基题）。调用方分散在三个文件，需要逐一确认而不是只看题面点名的那个。

## Reference solution
1. 搜索 format_waybill_no，命中 waybill.py（定义）与 dispatch_cli.py、sms_notify.py、archive.py。
2. 抽查确认三处都是真实调用。
3. 作答 3。

## Why the answer is unique
`format_waybill_no(` 的调用分别出现在 dispatch_cli.py、sms_notify.py、archive.py 三个文件；waybill.py 是定义所在，不算调用。按文件计数唯一。

## 正确答案
3
