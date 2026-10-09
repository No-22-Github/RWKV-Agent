## Traps
- TR-NEARNAME: 鼓浪屿 is an island district of 厦门, not a city; get_weather resolves cities, so asking for 鼓浪屿 returns location not found and the retry is 厦门.
- TR-DECOY: tomorrow is 30%; 后天 (2026-09-18) is 75%.

## Reference solution
1. get_weather {"location": "厦门", "days": 3} (or 鼓浪屿 first, then 厦门 after the not-found error)
Final answer: 后天（9 月 18 日）厦门有中雨，降水概率 75%，上鼓浪屿记得带伞；鼓浪屿属于厦门，按厦门的预报看。

## Why the answer is unique
后天 is the third forecast row; the island has no separate forecast.

## Five alternative phrasings of the task
1. 鼓浪屿后天天气怎么样？
2. 后天上鼓浪屿要带伞吗？
3. 厦门后天下不下雨？
4. 9 月 18 日鼓浪屿会下雨吗？
5. Will it rain on Gulangyu the day after tomorrow?
