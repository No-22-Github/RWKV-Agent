## Traps
- TR-RULEFILE: the closing threshold is the daily low (<= 8°C), not rain; tomorrow is sunny with 10% rain, so common sense says open.
- TR-DECOY: today's low is 9 (above the line); tomorrow's low is 7.

## Reference solution
1. list_files / read_file 球馆/开放规定.md
2. get_weather {"location": "哈尔滨", "days": 3}
Final answer: 不开放：哈尔滨明天最低气温 7°C，不高于规定的 8°C，室外球场关闭，只开室内馆；天晴、降水概率 10%，不是下雨的问题。

## Why the answer is unique
The low 7 is <= 8; the rule is explicit.

## Five alternative phrasings of the task
1. 哈尔滨球馆明天室外场开放吗
2. 明天室外球场能不能用，按规定
3. 按规定哈尔滨明天只开室内馆吗
4. 明天室外场地开放情况按规定怎么算
5. Under the rules, will the outdoor courts in Harbin be open tomorrow?
