## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 台账/三亚.txt; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 台账/三亚.txt (format)
2. get_weather {"location": "三亚", "days": 3}
3. write: '日期=2026-09-17 城市=三亚 天气=大雨 温度=17/30 降水=90%' / '日期=2026-09-18 城市=三亚 天气=小雨 温度=19/31 降水=70%'
4. read_file 台账/三亚.txt once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to 台账/三亚.txt in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把三亚天气按文件格式记下来
2. 三亚 的预报补到记录文件里
3. 照着已有行的格式写三亚的天气
4. 三亚天气记录更新一下
5. Add 三亚 weather to the log in its format
