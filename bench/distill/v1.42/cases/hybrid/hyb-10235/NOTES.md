## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 数据/天气.csv; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 数据/天气.csv (format)
2. get_weather {"location": "苏州", "days": 3}
3. write: '2026-09-17,苏州,阴,22,28,20'
4. read_file 数据/天气.csv once to confirm
Final answer: added the 2026-09-17 line(s) to 数据/天气.csv in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把苏州天气按文件格式记下来
2. 苏州 的预报补到记录文件里
3. 照着已有行的格式写苏州的天气
4. 苏州天气记录更新一下
5. Add 苏州 weather to the log in its format
