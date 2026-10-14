## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of dash/munich.jsonl; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file dash/munich.jsonl (format)
2. get_weather {"location": "Munich", "days": 3}
3. write: '{"date": "2026-09-17", "city": "Munich", "cond": "Light rain", "low": 10, "high": 24, "pop": 60}' / '{"date": "2026-09-18", "city": "Munich", "cond": "Overcast", "low": 13, "high": 18, "pop": 40}'
4. read_file dash/munich.jsonl once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to dash/munich.jsonl in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. Log Munich's forecast in the file's format
2. Update the Munich weather file
3. Append Munich weather like the other lines
4. Add the forecast lines for Munich
5. 把 Munich 的天气按格式写进文件
