## Traps
- TR-DEFN: turn 2 changes the city, so the 杭州 forecast (小雨 21~26°C 65%) must be replaced, not kept; both the 地点 line and the 天气 line change.
- TR-DECOY: 苏州 today is 阴 21~27°C 30% and the day after is 多云; only tomorrow's row (中雨 20~25°C 80%) belongs in the file.
Newline policy: only the named lines are replaced/appended, so every other line and the single trailing newline stay as they are.

## Reference solution
Turn 1: get_weather for the first city; edit the file; read_file to confirm.
Turn 2: get_weather for the new city/day (a different forecast is needed); edit the file again; read_file to confirm.
Final answer: 已把 行程/明日.md 改成苏州：地点是苏州，天气是中雨 20~25°C，降水概率 80%。

## Why the answer is unique
The line formats are fixed by the prompts; 明天 = 2026-09-17 is the second forecast row of each city.

## Five alternative phrasings of the task
1. 明天改去苏州，文件里的地点和天气一起换掉
2. 把明日出行改成苏州明天的预报
3. 杭州换成苏州，天气行用苏州明天的数据
4. 行程文件先填杭州天气，再改成苏州
5. Fill the trip note with Hangzhou's forecast, then change it to Suzhou.
