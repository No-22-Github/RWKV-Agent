# hyb-7735 NOTES

- 会话形状：派活后道谢再追问（第 1 轮 4 月首周出货量任务，第 2 轮道谢 + 追问 Northgate 的量）。
- 语言：英文。两轮都按数值判：第 1 轮答案 100，第 2 轮答案 75。

## Traps

- TR-DATEFMT: logs/april_dispatches.csv 的日期混用 ISO（2026-04-02）与 month/day/year（04/06/2026），README 写明斜杠式是美国式月/日/年。不注意会得到：把 04/06/2026 当成 6 月 4 日逐出首周，得 100 - 35 = 65（trap_decoys 记 65）；或把 03/28/2026、04/13/2026 误算进首周。

## Reference solution

1. 第 1 轮：读取 logs/april_dispatches.csv，README 写明两种日期写法（第 1 次工具调用）。
2. 解析日期并取 2026-04-01 至 04-07 的三行（2026-04-02、2026-04-05、04/06/2026），units 求和：40 + 25 + 35 = 100。
3. 第 2 轮：同一批三行里 destination 为 Northgate 的两行求和：40 + 35 = 75（第 2 次工具调用，重读同一文件；ref_calls = 2）。

## Why the answer is unique

65 来自把 04/06/2026 逐出首周，但 README 写明斜杠式是月/日/年，04/06 就是 4 月 6 日，必须计入；把 03/28/2026（3 月 28 日）或 04/13/2026（4 月 13 日）算进来分别得 155 或 160，都超出「前七日」。75 是首批三行中 Northgate 两行之和；把 Oakfield（55、60）或 Riverside（25）算进来不满足「Northgate」，把首周之外的 45（04-09）算进来得 120。答案分别只有 100 和 75。

## Five alternative phrasings

1. Sum the units dispatched in the first seven days of April 2026 from logs/april_dispatches.csv.
2. logs/april_dispatches.csv - how many cartons left the warehouse in April 1-7?
3. Tell me the total units shipped during the first week of April, final figure only.
4. How many units went out between April 1 and April 7, 2026? Log is at logs/april_dispatches.csv.
5. Give me the April first-week dispatch unit total from the log.
