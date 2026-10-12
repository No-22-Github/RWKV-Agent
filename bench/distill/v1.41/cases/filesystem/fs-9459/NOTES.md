## Traps
- TR-DEFN: the new file is created (not existing yet) with the example file's two-line layout; 后天 is the third row.
- TR-DECOY: 多云: today's row is 多云; the file is for the day after tomorrow (晴).

## Reference solution
1. get_weather {"location": "南宁", "days": 3}
2. read_file 天气/海口.txt (optional, format example)
3. write_file 天气/南宁.txt with "晴\n25~34°C\n"
4. read_file 天气/南宁.txt to confirm
Final answer: 已新建 天气/南宁.txt：第一行「晴」，第二行「25~34°C」，海口.txt 没动。

## Why the answer is unique
The forecast row for 2026-09-18 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. 仿照海口.txt 为南宁后天天气建一个南宁.txt
2. 天气目录里新增南宁.txt，内容是南宁后天预报，格式同海口
3. 南宁后天的天气按海口.txt 的写法存成新文件
4. 建 天气/南宁.txt，两行：天气和温度范围，数据取南宁后天
5. Create 天气/南宁.txt in the same two-line format as 海口.txt using Nanning's forecast for the day after tomorrow.
