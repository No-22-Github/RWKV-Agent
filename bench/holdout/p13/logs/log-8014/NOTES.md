## Traps
- TR-DECOY: 日志里 20:44:36（发布前）就有一条 db-primary 的 ERROR，发布记录里最近一次生产发布是 21:40 的 api-gateway v3.3.0，故障窗口应从 21:40 起算；窗口内最先报错的是 21:44:07 的 sms-gateway。db-primary 在窗口内报错次数最多（4 次）又有一条更早的记录，最容易被当成「最先出事的」。

## Reference solution
1. 读 发布记录.csv：环境为生产的最近一次开始时间是 2026-09-18 21:40（api-gateway v3.3.0）。
2. 在 app-20260918.log 里从 21:40 起找第一条 [ERROR] 行：21:44:07 sms-gateway connect timeout。
3. 回答服务代号：sms-gateway。

## Why the answer is unique
「这次故障」以最近一次生产发布为起点（发布记录里 21:40 之前的都是 9 月 17 日及更早的发布或预发），窗口内 ERROR 行按时间排序第一条就是 sms-gateway；20:44 的 db-primary ERROR 在发布之前，与本次故障无关，db-primary 在窗口内虽然报错最多但首条在 21:47。答案唯一为 sms-gateway。
