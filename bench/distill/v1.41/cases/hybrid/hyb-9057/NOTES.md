## Traps
- TR-RULEFILE: the pour threshold is the daily low (< 5°C), not rain; tomorrow is sunny with 5% rain, so common sense says go ahead.
- TR-DECOY: today's high is 16; the rule looks at the low, and tomorrow's low is 3.

## Reference solution
1. list_files / read_file 工地/浇筑规程.md
2. get_weather {"location": "沈阳", "days": 3}
Final answer: 不能安排：沈阳明天最低气温 3°C，低于规程的 5°C，暂停浇筑、改期；天晴、降水概率只有 5%，不是下雨的问题。

## Why the answer is unique
The low of 3°C is below 5°C; the rule is explicit.

## Five alternative phrasings of the task
1. 沈阳工地明天能浇筑吗
2. 明天沈阳浇筑按规程行不行
3. 沈阳明天要不要暂停浇筑
4. 明天浇混凝土，规程允许吗
5. Under the site rules, can we pour concrete in Shenyang tomorrow?
