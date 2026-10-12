## Traps
- TR-RULEFILE: the second clause is a heat limit (high >= 33°C); tomorrow is sunny with 5% rain, so common sense says the lawn is fine, but the high of 34°C moves it indoors.
- TR-DECOY: 照常: today's high is 31 and tomorrow looks dry; only the 34 high trips the rule.

## Reference solution
1. read_file 场地/婚礼规定.md (list_files first)
2. get_weather {"location": "合肥", "days": 2}
Final answer: 改室内：合肥明天最高气温 34°C，达到规定的 33°C，婚礼改到室内厅；虽然天晴、降水概率只有 5%。

## Why the answer is unique
High 34 >= 33 triggers the indoor clause; the prompt forbids the other verdict word.

## Five alternative phrasings of the task
1. 合肥明天草坪婚礼要不要改室内，按场地规定
2. 明天合肥的婚礼场地，规定怎么说
3. 按规定合肥明天婚礼改室内吗
4. 合肥草坪婚礼明天能不能照规定办
5. Under the venue rules, does tomorrow's Hefei lawn wedding move indoors?
