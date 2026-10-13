## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of notes/montreal.md; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file notes/montreal.md (format)
2. get_weather {"location": "Montreal", "days": 3}
3. write: '* **Thu 17 Sep** — Sunny, 15 to 19 °C (0% rain)' / '* **Fri 18 Sep** — Overcast, 9 to 18 °C (40% rain)'
4. read_file notes/montreal.md once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to notes/montreal.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. Log Montreal's forecast in the file's format
2. Update the Montreal weather file
3. Append Montreal weather like the other lines
4. Add the forecast lines for Montreal
5. 把 Montreal 的天气按格式写进文件
