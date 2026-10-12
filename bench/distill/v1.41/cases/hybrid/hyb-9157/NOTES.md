## Traps
- TR-DEFN: the status file holds exactly one line and has NO trailing newline, before and after; the line is for the day after tomorrow (2026-09-18, the third row), not tomorrow's 阵雨.
Newline policy: expected file is the bare line "拉萨|2026-09-18|晴|9~21|5%" with no newline at the end.

## Reference solution
1. get_weather {"location": "拉萨", "days": 3}
2. write_file 状态/天气.txt with the single line, no trailing newline
3. read_file 状态/天气.txt to confirm
Final answer: 已把拉萨后天（2026-09-18）的预报（晴，9~21°C，降水概率 5%）写进 状态/天气.txt，文件只有这一行、没有结尾换行。

## Why the answer is unique
后天 is the third forecast row; the single-line format is spelled out and the temperature range keeps the forecast's own form.

## Five alternative phrasings of the task
1. 拉萨后天的天气写进状态文件，只要一行
2. 状态/天气.txt 改成拉萨 9 月 18 日预报，不带结尾换行
3. 用拉萨后天预报覆盖天气.txt 那一行
4. 把拉萨后天天气按竖线格式写到状态文件
5. Replace the status line with Lhasa's forecast for the day after tomorrow, no trailing newline.
