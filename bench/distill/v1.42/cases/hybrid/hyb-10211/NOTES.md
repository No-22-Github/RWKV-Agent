## Traps
- TR-NEARNAME: 西湖 is a lake in 杭州, not a city: the lookup is 杭州.

## Reference solution
1. get_weather {"location": "杭州", "days": 3} -> 65%
Final answer: 西湖在杭州，杭州明天降水概率 65%。

## Why the answer is unique
The fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.

## Five alternative phrasings of the task
1. 西湖明天下雨吗
2. 明天游西湖要带伞吗
3. 杭州明天降水概率
4. 明天西湖天气
5. 去西湖散步，明天天气怎样
