## Traps
- TR-DEFN: two rows contain 待填; only the 09-17 row is filled and the table pipes and spacing stay the same.
- TR-DECOY: 多云: today's row is 多云; the row to fill is 09-17 (小雨).

## Reference solution
1. get_weather {"location": "成都", "days": 2}
2. replace_lines (or write_file) on 行程/行程表.md: the 09-17 row becomes "| 09-17 | 成都 | 小雨 | 20~25°C |"
3. read_file 行程/行程表.md to confirm
Final answer: 已把 09-17 那行填成「小雨 / 20~25°C」，09-18 那行仍是待填。

## Why the answer is unique
The forecast row for 2026-09-17 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. 行程表 09-17 那行填成都明天的天气和气温
2. 把行程/行程表.md 里 9 月 17 日的待填换成成都明天预报
3. 表格里 09-17 一行补上成都明天的天气，09-18 别动
4. 行程表的明天那行：天气和气温按成都预报填
5. Fill the 09-17 row of the itinerary table with Chengdu's forecast for tomorrow.
