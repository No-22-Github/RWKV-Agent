## Traps
- TR-DECOY: turn 2 asks 后天 (2026-09-18, third row) for 北京; 北京 tomorrow's high is 27 and 上海's numbers from turn 1 do not apply.

## Reference solution
Turn 1: get_weather for the first place, answer. Turn 2: get_weather for the new place (a second lookup is needed), answer.
Final answers: 上海明天最高 31°C；北京后天有阵雨（降水概率 70%），最高 24°C。

## Why the answer is unique
The fixed clock gives 明天 = 09-17 and 后天 = 09-18; each city has its own forecast rows.

## Five alternative phrasings of the task
1. 明天上海最高几度，后天北京呢？
2. 先告诉我上海明天最高温，再看北京后天会不会下雨
3. 上海明天高温多少；北京后天下雨吗、最高多少
4. 9 月 17 日上海最高气温，以及 9 月 18 日北京的天气
5. What is Shanghai's high tomorrow, and what about Beijing the day after?
