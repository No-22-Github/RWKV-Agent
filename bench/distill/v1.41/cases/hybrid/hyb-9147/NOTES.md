## Traps
- TR-NEARNAME: 亚龙湾 is a scenic spot / district of 三亚, not a city of its own; get_weather resolves cities only, so asking for 亚龙湾 returns location not found and the retry is 三亚 (asking for 三亚 straight away is equally good).
- TR-DECOY: 10%: today's rain chance is 10%; tomorrow (2026-09-17) is 70%.

## Reference solution
1. get_weather {"location": "三亚", "days": 3} (or 亚龙湾 first, then 三亚 after the not-found error; the same failing name is never retried)
Final answer: 亚龙湾属于三亚，三亚明天（9 月 17 日）有雷阵雨，降水概率 70%，气温 26~31°C，潜水行程建议改期或备好雨具。

## Why the answer is unique
亚龙湾 is a bay in 三亚; tomorrow is the second forecast row.

## Five alternative phrasings of the task
1. 亚龙湾明天降水概率是多少
2. 明天去亚龙湾潜水，下雨的可能性大吗
3. 9 月 17 日亚龙湾会下雨吗
4. 亚龙湾明天天气怎么样，会不会有雷雨
5. Will it rain at Yalong Bay tomorrow (亚龙湾)?
