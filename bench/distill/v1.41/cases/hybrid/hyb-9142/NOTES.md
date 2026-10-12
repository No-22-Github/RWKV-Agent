## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather (后天 is the third row) and 敦煌 莫高窟 旺季 套票 from web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 晴: today and tomorrow are 晴; only 后天 (2026-09-18) is 扬沙.

## Reference solution
1. get_weather {"location": "敦煌", "days": 3}
2. web_search 敦煌 莫高窟 旺季 套票
Final answer: 莫高窟旺季数字展示加实景洞窟套票 238 元，需提前预约；敦煌后天（9 月 18 日）有扬沙，10~22°C，降水概率 5%，出行带好口罩。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (238).

## Five alternative phrasings of the task
1. 敦煌莫高窟旺季套票多少钱，敦煌后天天气呢
2. 后天去敦煌，莫高窟门票要多少，那天天气好吗
3. 敦煌后天的天气，还有莫高窟旺季票价
4. 查查敦煌莫高窟套票价格，顺便看敦煌后天天气
5. 莫高窟旺季门票多少钱？敦煌后天有风沙吗
