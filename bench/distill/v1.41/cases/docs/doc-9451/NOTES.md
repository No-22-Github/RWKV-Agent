## Traps
- TR-DEFN: the new line goes after the existing four lines and must end with exactly one newline; tomorrow is the second forecast row.
- TR-DECOY: 阴: today's row is 阴; the line is for tomorrow (2026-09-17, 小雨).

## Reference solution
1. get_weather {"location": "上海", "days": 2}
2. append_file 日志/出行日志.md with "- 09-17 上海 小雨 18~24°C\n"
3. read_file 日志/出行日志.md to confirm
Final answer: 已在 日志/出行日志.md 末尾追加「- 09-17 上海 小雨 18~24°C」，原有内容没动。

## Why the answer is unique
The forecast row for 2026-09-17 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. 给出行日志加一条上海明天的天气
2. 日志/出行日志.md 最后补一行上海 9 月 17 日的预报，格式跟前面一样
3. 把上海明天的天气记到出行日志末尾
4. 出行日志续一行：上海明天天气，照已有行的写法
5. Append Shanghai's forecast for tomorrow as a new line at the end of the trip log.
