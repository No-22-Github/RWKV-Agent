## Traps
- TR-DEFN: turn 2 changes both day and city, so the heading line and the forecast line must both change; 周五 = 2026-09-18 = 后天, the third row of the 重庆 forecast (days >= 3).
- TR-DECOY: 重庆 tomorrow is 雷阵雨 24~31°C 60%; 成都 tomorrow was 阵雨 19~24°C 70% from turn 1.
Newline policy: only the named lines are replaced/appended, so every other line and the single trailing newline stay as they are.

## Reference solution
Turn 1: get_weather for the first city; edit the file; read_file to confirm.
Turn 2: get_weather for the new city/day (a different forecast is needed); edit the file again; read_file to confirm.
Final answer: 已把 运动/跑步计划.md 改成周五在重庆跑：天气是晴 25~34°C，降水概率 5%。

## Why the answer is unique
The heading text is dictated by the prompt and the forecast line comes from the third row of 重庆's forecast.

## Five alternative phrasings of the task
1. 跑步改到周五去重庆，标题和天气一起更新
2. 把跑步计划换成重庆后天的预报
3. 先填成都明天，再把计划挪到周五重庆
4. 跑步计划：周四成都改为周五重庆并更新天气
5. Move the run to Friday in Chongqing and update the weather line.
