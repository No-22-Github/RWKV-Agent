## Traps
- TR-ABSENT: KD-2 当天 08:02 被「removed for impeller rebuild」，10-10 才回装；台账写明它 10-09 一剂没跑、自己一条日志都没有，所以它的告警数无法统计，也不能报 0。
- TR-DECOY: 当天日志里的三条 calibration drift 全是顶班的 KD-2 spare 的。把 spare 的告警数当成 KD-2 的，就是诱饵答案。

## Reference solution
1. 列出 logs/：一份 dosing 事件日志和泵台账。
2. 读 logs/kalk-dosing-2026-10-09.log：KD-2 被拆下重建，spare 顶班；WARN 全标着 spare。
3. 读 maintenance/PUMP-LEDGER.md：KD-2 当天没跑、没日志；spare 的告警归 spare。
终答（2–4 句）：KD-2 logged nothing on Oct 9: it was removed that morning for an impeller rebuild and reinstalled the next day, so the pump never ran. The calibration warnings in that day's log all belong to KD-2 spare, which covered the schedule. If you need the spare's drift trend, say so and I will pull its numbers. 判据：包含 KD-2 和一个 removed/rebuild/did not run 说法，不得把 spare 的告警数报成 KD-2 的。

## Why the answer is unique
The three warnings are the nearest-looking data, but every WARN line names KD-2 spare as the source, and both the log's INFO line and the ledger state KD-2 was removed for a rebuild and ran no doses. Counting them for KD-2 would attribute another pump's calibration behaviour to it. Nothing else logs KD-2 events that day, so the only defensible reply is that KD-2 logged nothing and why.
