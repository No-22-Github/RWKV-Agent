## Traps
- TR-DECOY: 22:48 的 price-sync worker WARN（漂移 0.4%，已重新同步）比真正的故障更显眼地先出现。不注意会把它当成事故原因（trap_decoys 值 price-sync），而日志里真正的故障是 23:14 起 checkout 对 payments-gw 的 TLS 握手失败（证书过期），23:20 部署新证书后恢复。

## Reference solution
1. 读 logs/checkout-20260929.jsonl（1 次调用）。
2. 终答（英文，自然语言 2–3 句）：事故是 23:14 开始 checkout 到 payments-gw 的 TLS 握手失败（证书过期）；price-sync 那条 WARN 只是良性漂移并已自行恢复；23:20 新证书部署后熔断关闭、队列排空，服务恢复。

## Why the answer is unique
日志只有一条故障链：23:14/23:15 两次 upstream_error 指向 payments-gw 的证书过期，23:20 circuit_closed 收尾；22:48 的 WARN 自带 "resynced ok"，与 checkout 组件无关联字段。把事故归到 price-sync 与日志记录矛盾；判据的必含事实（payments-gw、23:14、TLS）只有在正确归因下才会同时出现。
