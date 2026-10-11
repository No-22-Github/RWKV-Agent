## Traps
- TR-DEFN: the old file holds another city and date; the whole file is overwritten, not appended to.
Newline policy: the prompt lists all six lines (including the blank second line) and says the file ends with exactly one newline after the last line; expected is those six lines joined by newlines plus one trailing newline.

## Reference solution
1. get_weather {"location": "重庆", "days": 3}
2. write_file 报告/天气速报.md (full new content)
3. read_file 报告/天气速报.md to confirm
Final answer: 已把重庆后天（2026-09-18）的预报（中雨，22~27°C）写进 报告/天气速报.md，旧内容已覆盖。

## Why the answer is unique
后天 is the third forecast row; the template is fully specified.

## Five alternative phrasings of the task
1. 重庆后天的天气重做一份速报
2. 用重庆后天预报覆盖 报告/天气速报.md
3. 天气速报改成重庆 9 月 18 日
4. 更新速报文件，城市换成重庆、日期后天
5. Rewrite the weather brief for Chongqing the day after tomorrow.
