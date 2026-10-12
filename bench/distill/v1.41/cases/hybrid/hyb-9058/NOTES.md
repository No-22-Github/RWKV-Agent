## Traps
- TR-RULEFILE: the cancel threshold is a rain chance >= 30%; the high of 29°C is fine, so 阵雨 alone does not reveal the 45% figure that decides it.
- TR-DECOY: today's rain chance is 20%; tomorrow's 45% crosses the 30% limit.

## Reference solution
1. list_files / read_file 园务/春秋游规定.md
2. get_weather {"location": "南昌", "days": 3}
Final answer: 不能去：南昌明天有阵雨，降水概率 45%，达到规定的 30%，春秋游取消、改期；最高气温 29°C 不是问题。

## Why the answer is unique
45% >= 30% triggers the cancel rule.

## Five alternative phrasings of the task
1. 明天南昌春游按规定能去吗
2. 幼儿园明天去公园，规定允许吗
3. 南昌明天春秋游要取消吗
4. 按园务规定，明天出行还是改期
5. Under the kindergarten rules, is tomorrow's park trip in Nanchang still on?
