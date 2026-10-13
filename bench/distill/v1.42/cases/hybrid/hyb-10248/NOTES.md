## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 出差/无锡.md; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 出差/无锡.md (format)
2. get_weather {"location": "无锡", "days": 3}
3. write: '| 2026-09-17 | 周四 | 大雨 | 17 | 31 | 95% |' / '| 2026-09-18 | 周五 | 雷阵雨 | 22 | 26 | 70% |'
4. read_file 出差/无锡.md once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to 出差/无锡.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把无锡天气按文件格式记下来
2. 无锡 的预报补到记录文件里
3. 照着已有行的格式写无锡的天气
4. 无锡天气记录更新一下
5. Add 无锡 weather to the log in its format
