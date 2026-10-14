## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 台账/重庆.txt; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 台账/重庆.txt (format)
2. get_weather {"location": "重庆", "days": 5}
3. write: '日期=2026-09-19 城市=重庆 天气=多云 温度=16/28 降水=25%' / '日期=2026-09-20 城市=重庆 天气=晴 温度=17/27 降水=0%'
4. read_file 台账/重庆.txt once to confirm
Final answer: added the 2026-09-19, 2026-09-20 line(s) to 台账/重庆.txt in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把重庆天气按文件格式记下来
2. 重庆 的预报补到记录文件里
3. 照着已有行的格式写重庆的天气
4. 重庆天气记录更新一下
5. Add 重庆 weather to the log in its format
