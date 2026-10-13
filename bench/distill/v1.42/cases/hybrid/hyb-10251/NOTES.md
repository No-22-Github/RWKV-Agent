## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of 站点/桂林.html; the tool's labels are not that format.
- Turn 2 adds only the next day; turn 1's line must not appear twice.
- The file ends with a newline; new lines go before `</ul>`, one per day, each ending in a newline.

## Reference solution
1. read_file 站点/桂林.html (format)
2. get_weather {"location": "桂林", "days": 3}
3. write: '    <li>9月17日 周四 多云 21–26°C</li>' / '    <li>9月18日 周五 阴 22–26°C</li>'
4. read_file 站点/桂林.html once to confirm
Final answer: added the 2026-09-17, 2026-09-18 line(s) to 站点/桂林.html in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.

## Five alternative phrasings of the task
1. 把桂林天气按文件格式记下来
2. 桂林 的预报补到记录文件里
3. 照着已有行的格式写桂林的天气
4. 桂林天气记录更新一下
5. Add 桂林 weather to the log in its format
