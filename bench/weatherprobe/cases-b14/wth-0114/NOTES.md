## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of notes/edinburgh.md; the tool's labels are not that format.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file notes/edinburgh.md (format)
2. get_weather {"location": "Edinburgh", "days": 3}
3. write: '* **Thu 17 Sep** — Sunny, 12 to 23 °C (10% rain)' / '* **Fri 18 Sep** — Heavy rain, 11 to 19 °C (95% rain)'
4. read_file notes/edinburgh.md once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to notes/edinburgh.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. Log Edinburgh's forecast in the file's format
2. Update the Edinburgh weather file
3. Append Edinburgh weather like the other lines
4. Add the forecast lines for Edinburgh
5. 把 Edinburgh 的天气按格式写进文件
