## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of trip/weather.log; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file trip/weather.log (format)
2. get_weather {"location": "Lisbon", "days": 3}
3. write: 'Thu 17 Sep | Lisbon | Thunderstorms | 13-23°C | rain 75%'
4. read_file trip/weather.log once to confirm
Final answer: added the 2026-09-17 line(s) to trip/weather.log in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. Log Lisbon's forecast in the file's format
2. Update the Lisbon weather file
3. Append Lisbon weather like the other lines
4. Add the forecast lines for Lisbon
5. 把 Lisbon 的天气按格式写进文件
