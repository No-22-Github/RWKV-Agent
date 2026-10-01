## Traps
- 无陷阱（L0 基题）：这份扫描日志只覆盖 9 月 8-10 日，末行是周滚动说明，12 日在下一个卷文件 dock-scans-2026-09-11-14.log 里，而那个文件不在本工作区——要查的那天没有数据。卷内倒是有 2 条 DOCK_LATE（9 月 8、9 日），是日期张冠李戴的天然错法。

## Reference solution
1. 读 README.md 的滚动说明，再读 logs/dock-scans-2026-09-08-10.log。
2. 确认覆盖范围：首行卷头、末行滚动说明，扫描只到 9 月 10 日；12 日不在这份文件里。
3. 终答两到三句（allocation v1.3 §4.1 第一行）：查了哪个文件、要查的日期无数据、给下一步。参考措辞：「logs/dock-scans-2026-09-08-10.log 只覆盖 9 月 8 日到 10 日（末行的滚动说明也写明下一卷是 11-14 日），12 日的 DOCK_LATE 次数无从统计。下一卷 dock-scans-2026-09-11-14.log 在 depot 共享上、没有拷进这个工作区，建议把它拿过来我再补这个数。」判分用 output_contains_any（DOCK_LATE 或 dock late）；output_excludes 排除 UNKNOWN 与「我没有工具」类说法。

## Why the answer is unique
卷头与 README 的滚动说明一致、扫描行最晚到 9 月 10 日，所以 12 日在这份文件里没有任何记录——不存在能从这份文件数出 12 日 DOCK_LATE 的读法。卷内 9 月 8、9 日的 2 条 DOCK_LATE 属于别的日期，把它们算进 12 日正是本题要卡的错误。可接受的写法都点名 12 日无数据。
