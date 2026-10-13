## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-17, row 2) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "杭州", "days": 3} -> 小雨
2. web_search 游船
Final answer: 西湖手划船每船每小时 150 元；杭州明天小雨。

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. 西湖手划船多少钱，杭州明天天气
2. 明天去西湖划船，价格和天气
3. 杭州明天天气，西湖手划船收费
4. 查西湖手划船价格，再看杭州明天天气
5. 西湖划船一小时多少钱？明天下雨吗
