## Traps
- TR-ABSENT: logs/flatwork-1/2026-09-09.log records "hall rewiring, log collection offline" at 10:48 and "collection back online; entries from 10:48 to 12:34 were not collected and are not backfilled" at 12:34. There is no line at all between 11:00 and 12:00; reading the empty hour as 0 stops is the decoy answer.


## Reference solution
1. Read logs/flatwork-1/2026-09-09.log: no lines between 10:48 and 12:34, and the collector itself says the gap is not backfilled.
2. Read ops/collector-notes.md: the collector goes offline during power work, does not backfill, and the controller keeps its event buffer for 7 days.
Final answer (2-4 sentences): the 11:00-12:00 stretch of the log is empty - the hall collector went offline for the rewiring at 10:48 and only came back at 12:34, and that window is not backfilled, so the jam-stop count for the hour cannot be determined and must not be read as 0. The ironer controller keeps its event buffer for 7 days; dump it over the service link to count the stops. (Reference: 15 jam stops appear ahead of the gap.) Criteria: mentions the pause/gap and must not report 0 stops.


## Changelog
- v2：去掉零次排除、扩缺口词表：老师答「不能报 0 次，是数据缺失」被「 0 次」误判；直接报 0 的终答由逐条阅读剔除。

## Why the answer is unique
The decoy 0 mistakes "not collected" for "did not happen": the log states the entries in the window were not collected and are not backfilled, and the collector notes confirm the same. No other source in the workspace covers the hour, so the count is unknowable and the only defensible reply names the gap and points at the controller buffer.
