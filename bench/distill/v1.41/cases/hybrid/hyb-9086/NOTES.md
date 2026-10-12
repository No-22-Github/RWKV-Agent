## Traps
- TR-RULEFILE: the rain threshold is 20%, lower than common sense; tomorrow is only 多云 with 25%, so it looks dry enough.
- TR-DECOY: today's rain chance is 15% (would pass); tomorrow's is 25%.

## Reference solution
1. list_files / read_file 农场/晾晒规定.md
2. get_weather {"location": "南宁", "days": 3}
Final answer: 不能晒：南宁明天降水概率 25%，达到规定的 20%，谷子收进仓；最高气温 34°C 不是问题。

## Why the answer is unique
25% >= 20% triggers the no-drying rule.

## Five alternative phrasings of the task
1. 南宁明天晒谷子行不行
2. 按规定明天稻谷要收仓吗
3. 明天南宁晒场能用吗
4. 稻谷明天晒还是收，按农场规定
5. Under the farm rules, can we dry rice on the yard in Nanning tomorrow?
