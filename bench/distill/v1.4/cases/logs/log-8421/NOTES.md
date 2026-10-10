## Traps
- TR-TZ: the window is given in Dubai time, the log in timestamps are UTC. Counting SHUTTER_FAULT lines whose log clock falls between the same clock numbers gives a different (wrong) count.
- TR-DECOY: SHUTTER_WARN lines are a different, similar event type and are not counted.

## Reference solution
1. Convert the window to the log clock: 2026-03-12 18:30 to 2026-03-12 22:30 UTC.
2. search_text for "SHUTTER_FAULT" in observatory/dome.log, then count the hits stamped inside that UTC range: 8.
Final answer, one sentence: 8 SHUTTER_FAULT events in the window. Criteria: the count 8 (number with a unit word); search_text used; at most one read_file.

## Changelog
- v2：S5：read_file 上限 1→2（对表题要读设备日志和服务端日志两份文件）；英文计数题改为 token 只认数字本身（老师常以「6.」开头）；终答上限 400→600（老师要写清换算口径和区间边界，三遍里多次超 400 被判挂）。

## Why the answer is unique
Window start is inclusive and end exclusive; every counted line sits at least 6 minutes inside a boundary, so the count is 8.
