## Traps
- TR-DEFN: two files say 待填; tomorrow's file is selected by its date name, the day-after-tomorrow file stays.
- TR-DECOY: 多云: today's row is 多云; the right file is 2026-09-17.txt (雷阵雨), and 2026-09-18.txt also says 待填 but must stay.

## Reference solution
1. get_weather {"location": "深圳", "days": 2}
2. write_file 日报/2026-09-17.txt with "天气：雷阵雨 26~32°C\n"
3. read_file 日报/2026-09-17.txt to confirm
Final answer: 已把 日报/2026-09-17.txt 改成「天气：雷阵雨 26~32°C」，其他日期的文件没动。

## Why the answer is unique
The forecast row for 2026-09-17 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. 日报里明天的文件填上深圳明天的天气
2. 把 2026-09-17 那天的日报天气一行改成深圳预报
3. 日报目录中明天那份，天气一栏按深圳明天预报写
4. 深圳明天的天气写进明天日期的日报文件
5. Write Shenzhen's forecast for tomorrow into tomorrow's file in the daily-report folder.
