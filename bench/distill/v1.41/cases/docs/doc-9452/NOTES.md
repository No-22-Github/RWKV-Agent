## Traps
- TR-DEFN: only the placeholder (with its brackets) is replaced, the rest of the line and file stay byte-identical.
- TR-DECOY: 阴: today's row is 阴; the placeholder is for tomorrow (阵雨).

## Reference solution
1. get_weather {"location": "苏州", "days": 2}
2. replace_lines (or write_file) on 简报/出差简报.md: the line becomes "- 明天天气：阵雨 24~28°C"
3. read_file 简报/出差简报.md to confirm
Final answer: 已把简报里的「【待填】」换成「阵雨 24~28°C」，其他行没动。

## Why the answer is unique
The forecast row for 2026-09-17 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. 出差简报里的待填换成苏州明天的天气
2. 简报/出差简报.md 的明天天气那行填上苏州 9 月 17 日预报
3. 把简报中的【待填】改成苏州明天的天气和温度
4. 出差简报补全：明天天气一栏写苏州明天的预报
5. Fill the placeholder on the tomorrow-weather line of the brief with Suzhou's forecast.
