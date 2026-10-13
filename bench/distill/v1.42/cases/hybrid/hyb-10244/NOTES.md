## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of data/berlin.csv; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file data/berlin.csv (format)
2. get_weather {"location": "Berlin", "days": 3}
3. write: '2026-09-17,Berlin,Drizzle,12,19,50' / '2026-09-18,Berlin,Sunny,15,24,10'
4. read_file data/berlin.csv once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to data/berlin.csv in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. Log Berlin's forecast in the file's format
2. Update the Berlin weather file
3. Append Berlin weather like the other lines
4. Add the forecast lines for Berlin
5. 把 Berlin 的天气按格式写进文件
