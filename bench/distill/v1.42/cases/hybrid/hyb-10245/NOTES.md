## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of trip/seoul.log; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file trip/seoul.log (format)
2. get_weather {"location": "Seoul", "days": 4}
3. write: 'Sat 19 Sep | Seoul | Thunderstorms | 12-18°C | rain 65%'
4. read_file trip/seoul.log once to confirm
Final answer: added the 2026-09-19 line(s) to trip/seoul.log in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. Log Seoul's forecast in the file's format
2. Update the Seoul weather file
3. Append Seoul weather like the other lines
4. Add the forecast lines for Seoul
5. 把 Seoul 的天气按格式写进文件
