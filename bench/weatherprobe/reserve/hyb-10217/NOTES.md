## Traps
- TR-DECOY: turn 2: 周日 is 2026-09-20 (row 5); a 3-day lookup from turn 1 does not cover it.

## Reference solution
Turn 1:. get_weather {"location": "大连", "days": 3} -> 26
Turn 2:. get_weather {"location": "大连", "days": 5} -> 22
Final answer: 大连周日（9 月 20 日）最高 22°C。

## Why the answer is unique
The fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.

## Five alternative phrasings of the task
1. 大连周日最高温
2. 周日大连多少度
3. 大连 9 月 20 日气温
4. 周日下午到大连热吗
5. 大连这个周日天气
