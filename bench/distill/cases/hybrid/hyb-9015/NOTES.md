## Traps
- TR-DEFN: the example row carries a weekday; 2026-09-16..18 are 周三..周五, which the forecast does not state.
Lesson: closing the loop -- weather in hand, write the artifact instead of searching more (2026-10-09 App failure).

## Reference solution
1. read_file 行程/青岛.md (example row format)
2. get_weather {"location": "青岛", "days": 3}
3. replace_lines / write_file: three rows under the example line
4. read_file 行程/青岛.md once to confirm
Final answer: 已把青岛 9 月 16–18 日的天气按示例格式写进 行程/青岛.md 的「天气」小节（周五有小雨）。

## Why the answer is unique
Row format comes from the example line; dates and weekdays follow the fixed clock.

## Five alternative phrasings of the task
1. 把青岛未来三天天气补进行程文件
2. 青岛三天天气写到行程的天气小节
3. 按示例格式记录青岛这三天的天气
4. 行程/青岛.md 的天气部分帮我填上
5. Fill in the Qingdao trip note with the 3-day forecast.
