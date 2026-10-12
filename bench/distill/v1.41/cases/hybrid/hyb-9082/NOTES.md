## Traps
- TR-DEFN: the old file holds another city and date; the whole file is overwritten. Tomorrow is the second row, not today's.
Newline policy: six lines (second is blank) joined by newlines plus exactly one trailing newline.

## Reference solution
1. get_weather {"location": "西宁", "days": 3}
2. write_file 出行/提示.md with the six lines
3. read_file 出行/提示.md to confirm
Final answer: 已把西宁明天（2026-09-17）的预报（小雨，6~15°C）写进 出行/提示.md，旧内容已覆盖。

## Why the answer is unique
明天 is the second forecast row; the layout is fully specified.

## Five alternative phrasings of the task
1. 西宁明天的天气更新到出行提示
2. 用西宁明天预报覆盖 出行/提示.md
3. 出行提示改成西宁 9 月 17 日
4. 把提示文件换成西宁明天的天气
5. Rewrite the travel note with Xining's forecast for tomorrow.
