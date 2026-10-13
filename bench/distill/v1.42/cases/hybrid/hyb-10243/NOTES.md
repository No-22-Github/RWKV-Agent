## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 出差/天津.md; the tool's labels are not that format.
- Today's row is already in the file; writing it again is a duplicate.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 出差/天津.md (format)
2. get_weather {"location": "天津", "days": 3}
3. write: '| 2026-09-17 | 周四 | 阵雨 | 22 | 26 | 65% |'
4. read_file 出差/天津.md once to confirm
Final answer: added the 2026-09-17 line(s) to 出差/天津.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把天津天气按文件格式记下来
2. 天津 的预报补到记录文件里
3. 照着已有行的格式写天津的天气
4. 天津天气记录更新一下
5. Add 天津 weather to the log in its format
