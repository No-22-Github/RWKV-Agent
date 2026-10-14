## Traps
- TR-DECOY: turn 1's value (中雨) is for 张家界; turn 2 needs 凤凰's own report.

## Reference solution
Turn 1:. get_weather {"location": "张家界", "days": 3} -> 中雨
Turn 2:. get_weather {"location": "凤凰", "days": 3} -> 雷阵雨
Final answer: 凤凰：雷阵雨。

## Why the answer is unique
The fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.

## Five alternative phrasings of the task
1. 张家界和凤凰两地天气
2. 先查张家界再查凤凰
3. 张家界天气怎样，再看凤凰
4. 凤凰 的天气呢
5. Compare 张家界 and 凤凰 weather
