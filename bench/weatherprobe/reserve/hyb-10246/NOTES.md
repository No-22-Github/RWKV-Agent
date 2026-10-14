## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 台账/宁波.txt; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 台账/宁波.txt (format)
2. get_weather {"location": "宁波", "days": 3}
3. write: '日期=2026-09-17 城市=宁波 天气=阵雨 温度=17/31 降水=65%'
4. read_file 台账/宁波.txt once to confirm
Final answer: added the 2026-09-17 line(s) to 台账/宁波.txt in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把宁波天气按文件格式记下来
2. 宁波 的预报补到记录文件里
3. 照着已有行的格式写宁波的天气
4. 宁波天气记录更新一下
5. Add 宁波 weather to the log in its format
