## Traps
- TR-RULEFILE: the go/no-go thresholds are in 规则/户外活动.md (high >= 33°C or rain >= 50%); 郑州 tomorrow is clear (10% rain) but its high 34°C crosses the heat limit, so common sense on rain alone says go outdoors.
- TR-DECOY: today's high is 31 (would pass).

## Reference solution
1. list_files / read_file 规则/户外活动.md
2. get_weather {"location": "郑州", "days": 3}
Final answer: 不能照常户外：郑州明天最高气温 34°C，达到规则里 33°C 的上限，户外拓展改到室内；降水概率只有 10%，不是雨的问题。

## Why the answer is unique
The rule and the forecast together decide; only the high temperature triggers it.

## Five alternative phrasings of the task
1. 郑州明天户外活动要不要改室内？
2. 明天郑州的拓展训练还能在外面搞吗
3. 按学校规定，明天户外课行不行
4. 明天郑州户外活动按规则怎么安排
5. Can tomorrow's outdoor activity in Zhengzhou go ahead under our rules?
