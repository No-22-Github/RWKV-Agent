## Traps
- TR-RULEFILE: the threshold is in 工地/施工规定.md

## Reference solution
1. get_weather {"location": "南宁", "days": 3} -> 60%
Final answer: 不能：南宁后天小雨，降水概率 60%，超过 50% 的限制。

## Why the answer is unique
The fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.

## Five alternative phrasings of the task
1. 后天南宁能浇混凝土吗
2. 按规定后天能施工吗
3. 南宁后天降水概率
4. 后天浇筑条件满足吗
5. 南宁 9 月 18 日能浇筑吗
