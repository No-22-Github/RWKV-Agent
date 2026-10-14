## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 笔记/广州天气.md; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 笔记/广州天气.md (format)
2. get_weather {"location": "广州", "days": 3}
3. write: '- 09-18（周五）广州：雷阵雨，22~30℃，降水 80%'
4. read_file 笔记/广州天气.md once to confirm
Final answer: added the 2026-09-18 line(s) to 笔记/广州天气.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把广州天气按文件格式记下来
2. 广州 的预报补到记录文件里
3. 照着已有行的格式写广州的天气
4. 广州天气记录更新一下
5. Add 广州 weather to the log in its format
