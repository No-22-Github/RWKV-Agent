## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 日记/扬州.md; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 日记/扬州.md (format)
2. get_weather {"location": "扬州", "days": 3}
3. write: '9月17日（周四），扬州，中雨，最高 29 度。' / '9月18日（周五），扬州，阵雨，最高 30 度。'
4. read_file 日记/扬州.md once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to 日记/扬州.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把扬州天气按文件格式记下来
2. 扬州 的预报补到记录文件里
3. 照着已有行的格式写扬州的天气
4. 扬州天气记录更新一下
5. Add 扬州 weather to the log in its format
