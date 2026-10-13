## Traps
- TR-DECOY: turn 1's value (80%) is for 威海; turn 2 needs 杭州's own report.
- 西湖 is in 杭州; the lookup is 杭州.

## Reference solution
Turn 1:. get_weather {"location": "威海", "days": 3} -> 80%
Turn 2:. get_weather {"location": "杭州", "days": 3} -> 50%
Final answer: 杭州：50%。

## Why the answer is unique
The fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.

## Five alternative phrasings of the task
1. 威海和杭州两地天气
2. 先查威海再查杭州
3. 威海天气怎样，再看杭州
4. 杭州 的天气呢
5. Compare 威海 and 杭州 weather
