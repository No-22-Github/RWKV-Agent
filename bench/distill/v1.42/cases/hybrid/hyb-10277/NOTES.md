## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-18, row 3) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "武汉", "days": 3} -> 55%
2. web_search 黄鹤楼
Final answer: 黄鹤楼成人票 70 元；武汉后天降水概率 55%。

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. 黄鹤楼门票多少钱，武汉后天天气
2. 后天去黄鹤楼，票价和天气
3. 武汉后天下雨吗，黄鹤楼成人票价
4. 查黄鹤楼票价，再看武汉后天降水
5. 黄鹤楼要多少钱？后天武汉天气
