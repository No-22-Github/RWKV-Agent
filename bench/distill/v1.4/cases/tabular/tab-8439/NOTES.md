## Traps
- TR-DATEFMT: the dep column mixes 2026/10/xx, dd-10-2026 (day-month-year per the README), Oct d, 2026 and ISO timestamps. Reading dd-mm as mm-dd moves those rows out of the range and gives 22.
- TR-HEADER: the column names are not obvious (booking, dep, hull, usd); a wrong name returns a field-missing error and must be corrected and retried.

## Reference solution
1. data_query: path charters/bookings.csv, group_by dep, operation count; at most 40 groups come back.
2. Normalise every group to a day of month 10 using the README; keep days 5 to 7 inclusive (8 distinct cell values in range).
3. Add them up with the calculator: 33.
Final answer, 1-2 sentences: the result is 33 bookings (as the question asks), noting the date column mixes formats and the dd-mm-yyyy cells were read as day-month-year per the README. Criteria: value (spellings in any), data_query used, at most one read_file.

## Changelog
- v2：S5：去掉 required data_query（表里日期混用三四种写法，data_query 只做等值筛选、没法归一日期，老师整读后按日期归并手算才是对的路径）；read_file 上限 1→2（README 说明日期写法，先读 README 再读表是正常路径）；计数题词表补「N 个 / N 条」；终答上限 500→600。

## Why the answer is unique
The README fixes how the short dates read and ISO timestamps are UTC 08:00 on the same day, so each cell maps to exactly one day of month 10; both range ends are inclusive.
