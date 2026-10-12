## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 秦始皇帝陵博物院 兵马俑 旺季 门票 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 晴: today is 晴; only 后天 (2026-09-18) is 大雨.

## Reference solution
1. get_weather {"location": "西安", "days": 3}
2. web_search 秦始皇帝陵博物院 兵马俑 旺季 门票
Final answer: 兵马俑旺季门票 120 元，需提前实名预约；西安后天（9 月 18 日）有大雨，降水概率 85%，17~22°C，记得带雨具。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (120).

## Five alternative phrasings of the task
1. 兵马俑旺季门票多少钱，西安后天天气呢
2. 后天去西安，兵马俑票价是多少，那天会下雨吗
3. 西安后天的天气，还有兵马俑门票
4. 查查兵马俑旺季票价，顺便看西安后天天气
5. 兵马俑现在门票多少？西安后天有雨吗
