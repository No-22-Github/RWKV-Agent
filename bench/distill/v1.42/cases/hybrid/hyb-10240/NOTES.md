## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 日记/天气.md; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 日记/天气.md (format)
2. get_weather {"location": "武汉", "days": 3}
3. write: '9月17日（周四），武汉，阵雨，最高 27 度。'
4. read_file 日记/天气.md once to confirm
Final answer: added the 2026-09-17 line(s) to 日记/天气.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把武汉天气按文件格式记下来
2. 武汉 的预报补到记录文件里
3. 照着已有行的格式写武汉的天气
4. 武汉天气记录更新一下
5. Add 武汉 weather to the log in its format
