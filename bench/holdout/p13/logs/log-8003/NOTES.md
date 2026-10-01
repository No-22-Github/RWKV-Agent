## Traps
- 无陷阱（L0）。要点：答案是一段 2–5 句的中文自然语言总结，必须落在导出的真实内容上：payments-api 在 02:14 对 clearing-gw 出现 3 次网关超时，02:19 自动恢复（排队订单重放成功），orders-api 心跳正常。只说「整体稳定」而漏掉超时事件与恢复结局的答案过不了判据。

## Reference solution
1. 读 watchdog-export.jsonl（1 次调用）。
2. 终答（中文，自然语言 2–4 句）：昨晚整体平稳；唯一的波动是 payments-api 在 02:14 前后对 clearing-gw 的 3 次超时，02:19 自动恢复、排队订单已重放成功；orders-api 心跳正常（p99 212ms）；早上会可顺带确认 clearing-gw 侧当时的状态。

## Why the answer is unique
导出共四条记录且互不冲突：meta 说明窗口，事件给出超时次数与恢复时间，heartbeat 给出正常信号。「稳不稳」的答案由这些记录唯一决定；判据的必含事实（payments-api、02:14、恢复）只能来自读事件记录，编造别的事故或漏掉恢复结局都过不了。
