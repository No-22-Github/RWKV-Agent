## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 数据/珠海.csv; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 数据/珠海.csv (format)
2. get_weather {"location": "珠海", "days": 3}
3. write: '2026-09-17,珠海,多云,19,30,25' / '2026-09-18,珠海,阴,17,30,30'
4. read_file 数据/珠海.csv once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to 数据/珠海.csv in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把珠海天气按文件格式记下来
2. 珠海 的预报补到记录文件里
3. 照着已有行的格式写珠海的天气
4. 珠海天气记录更新一下
5. Add 珠海 weather to the log in its format
