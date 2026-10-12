## Traps
- TR-DEFN: the old file is another city and date; the whole file is overwritten with one compact JSON line (keys in the given order, no spaces, low/high bare integers). Tomorrow is the second row, not today's.
Newline policy: exactly one line, ending with one newline; nothing else in the file.

## Reference solution
1. get_weather {"location": "乌鲁木齐", "days": 2}
2. write_file 数据/forecast.json with {"city":"乌鲁木齐","date":"2026-09-17","condition":"多云","low":9,"high":24} plus a trailing newline
3. read_file 数据/forecast.json to confirm
Final answer: 已把乌鲁木齐明天（2026-09-17）的预报（多云，9~24°C）写进 数据/forecast.json，旧内容已覆盖。

## Why the answer is unique
明天 is the second forecast row; the JSON layout is fully specified.

## Five alternative phrasings of the task
1. 把乌鲁木齐明天的预报写成 JSON 放进 数据/forecast.json
2. 用乌鲁木齐明天预报覆盖 forecast.json，格式见上
3. forecast.json 改成乌鲁木齐 9 月 17 日的预报
4. 乌鲁木齐明天天气写入 JSON 文件，一行就行
5. Overwrite forecast.json with Urumqi's forecast for tomorrow as one JSON line.
