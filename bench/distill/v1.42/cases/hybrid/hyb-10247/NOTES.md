## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 笔记/烟台天气.md; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go at the end, one per day, each ending in a newline.

## Reference solution
1. read_file 笔记/烟台天气.md (format)
2. get_weather {"location": "烟台", "days": 3}
3. write: '- 09-17（周四）烟台：中雨，18~25℃，降水 90%' / '- 09-18（周五）烟台：大雨，18~29℃，降水 95%'
4. read_file 笔记/烟台天气.md once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to 笔记/烟台天气.md in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把烟台天气按文件格式记下来
2. 烟台 的预报补到记录文件里
3. 照着已有行的格式写烟台的天气
4. 烟台天气记录更新一下
5. Add 烟台 weather to the log in its format
