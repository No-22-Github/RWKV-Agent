## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 看板/weather.jsonl; the tool's labels are not that format.
- Today's row is already in the file; writing it again is a duplicate.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 看板/weather.jsonl (format)
2. get_weather {"location": "深圳", "days": 3}
3. write: '{"date": "2026-09-17", "city": "深圳", "cond": "阴", "low": 19, "high": 31, "pop": 30}' / '{"date": "2026-09-18", "city": "深圳", "cond": "小雨", "low": 17, "high": 25, "pop": 60}'
4. read_file 看板/weather.jsonl once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to 看板/weather.jsonl in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把深圳天气按文件格式记下来
2. 深圳 的预报补到记录文件里
3. 照着已有行的格式写深圳的天气
4. 深圳天气记录更新一下
5. Add 深圳 weather to the log in its format
