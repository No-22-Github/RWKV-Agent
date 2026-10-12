## Traps
- TR-RULEFILE: the 30°C heat threshold and the early-morning alternative live in 社团/晨跑规则.md; rain is only 10%, so skipping the file suggests training as planned.
- TR-DECOY: today's high is 30 (also at the limit); tomorrow's 31 is what counts.

## Reference solution
1. list_files / read_file 社团/晨跑规则.md
2. get_weather {"location": "济南", "days": 3}
Final answer: 不能按原计划：济南明天最高气温 31°C，达到规则的 30°C 上限，训练改到早上 6 点至 7 点；降水概率 10%，不影响。

## Why the answer is unique
Tomorrow's high 31 triggers the heat rule; rain does not trigger.

## Five alternative phrasings of the task
1. 明天济南晨跑社训练时间要不要改
2. 按社团规则，明天下午的训练照常吗
3. 济南明天晨跑社怎么安排
4. 明天训练按规则改早上还是照旧
5. Under our club rules, does tomorrow's training in Jinan stay at 5 pm?
