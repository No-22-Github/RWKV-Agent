## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast from get_weather (明天 is the second row) and 大连国际马拉松 报名费 from web search; the weather part must not be searched.
- TR-DECOY: the web page also lists last year's fee 168; today's weather is 多云 (not tomorrow's).

## Reference solution
1. get_weather {"location": "大连", "days": 2}
2. web_search 大连国际马拉松 报名费
Final answer: 大连明天（9 月 17 日）有雷阵雨，降水概率 65%，17~22°C，晨跑建议改室内；2026 大连国际马拉松全程报名费 198 元（去年 168 元），9 月 28 日截止。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value.

## Five alternative phrasings of the task
1. 大连明天天气如何？还有大马全程报名费多少
2. 查查大连国际马拉松全马报名费，顺便看明天大连天气
3. 明早大连跑步天气，加上马拉松报名价格
4. 大连明天会下雨吗，马拉松报名要多少钱
5. Dalian weather tomorrow and the marathon entry fee?
