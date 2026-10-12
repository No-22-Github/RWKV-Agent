## Traps
- TR-DEFN: the whole file is overwritten (the old 出门带伞 line disappears); today is the first forecast row; the rain chance keeps its % sign.
- TR-DECOY: 雷阵雨: tomorrow is 雷阵雨; today (2026-09-16) is 多云.

## Reference solution
1. get_weather {"location": "武汉", "days": 1}
2. write_file 提醒/今日提醒.txt with "武汉今天：多云\n气温 21~30°C，降水概率 20%\n"
3. read_file 提醒/今日提醒.txt to confirm
Final answer: 已把 提醒/今日提醒.txt 覆盖成武汉今天的两行预报：多云，21~30°C，降水概率 20%。

## Why the answer is unique
The forecast row for 2026-09-16 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. 用武汉今天的天气覆盖今日提醒.txt，两行
2. 今日提醒改成武汉今天的天气和气温、降水概率
3. 提醒文件重写：第一行武汉今天天气，第二行气温和降水概率
4. 把今日提醒的内容换成武汉今天的预报，格式见上
5. Overwrite the reminder note with Wuhan's forecast for today in two lines.
