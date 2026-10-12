## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 黄山 云谷索道 上行 单程 票价 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 多云: tomorrow is 多云; only 后天 (2026-09-18) is 大雾.

## Reference solution
1. get_weather {"location": "黄山", "days": 3}
2. web_search 黄山 云谷索道 上行 单程 票价
Final answer: 黄山云谷索道上行单程 80 元；黄山后天（9 月 18 日）有大雾，降水概率 30%，12~19°C，山上能见度低，记得多带件外套。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (80).

## Five alternative phrasings of the task
1. 云谷索道上行一趟多少钱，黄山后天天气如何
2. 后天坐云谷索道上山，票价多少，天气怎样
3. 黄山后天的天气，还有云谷索道上行票价
4. 查下云谷索道上行单程价格，顺便看黄山后天天气
5. 云谷索道单程上山要多少钱？黄山后天有雾吗
