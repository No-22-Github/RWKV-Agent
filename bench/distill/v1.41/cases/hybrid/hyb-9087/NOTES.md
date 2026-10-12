## Traps
- TR-RULEFILE: the postponement threshold is rain >= 50%; tomorrow is 阵雨 with 55%, while the high of 16°C is far from the heat limit.
- TR-DECOY: today's rain chance is 20%; tomorrow's 55% crosses the 50% limit.

## Reference solution
1. list_files / read_file 学校/运动会规定.md
2. get_weather {"location": "长春", "days": 3}
Final answer: 不能如期举行：长春明天有阵雨，降水概率 55%，达到规定的 50%，运动会延期。

## Why the answer is unique
55% >= 50% triggers postponement.

## Five alternative phrasings of the task
1. 长春明天运动会要延期吗
2. 按规定明天运动会照常吗
3. 运动会明天办不办，规定怎么说
4. 长春学校明天运动会按规定行不行
5. Under the school rules, does tomorrow's sports day in Changchun go ahead?
