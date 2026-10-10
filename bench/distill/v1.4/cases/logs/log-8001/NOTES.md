## Traps
- TR-ABSENT: logs/payment-gw/2026-09-14.log 在 01:47 记录「collector: shipping paused for maintenance window」，03:41 记录「shipping resumed; lines from 01:47 to 03:41 were not shipped and are not backfilled」。2 点到 3 点之间一行都没有。把「没有超时行」读成「0 次超时」就是诱饵答案（0）。

## Reference solution
1. 读 logs/payment-gw/2026-09-14.log（或按 timeout 搜索后再看 01:47–03:41 前后的行），发现 01:47 到 03:41 没有日志，且 collector 说明这段不补传。
2. 读 运维/日志采集说明.md：暂停时段的日志不补传，原始日志只在网关本机 /var/log/gw/ 保留 7 天。
终答（2–4 句）：2 点到 3 点这一段日志是空的——collector 01:47 起因维护暂停推送、03:41 才恢复，这段不补传，所以没法统计超时次数，也不能当成 0 次；日志头写明主机是 gw-02，原始日志在本机 /var/log/gw/ 只保留 7 天，需要尽快去那台机器上取。（参考：1 点到 1 点 47 分有 5 次超时。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 次。

## Why the answer is unique
诱饵 0 错在把「没有记录」当成「没有发生」：日志自己写明 01:47–03:41 的行没有推送也不补传，采集说明也确认维护期间推送暂停。工作区里没有任何其他来源记录这一小时，所以次数无法确定，只能说明缺口并指向本机原始日志。
