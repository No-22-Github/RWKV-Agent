## Traps
- TR-MULTISRC: two sub-requests with two different sources -- the forecast from get_weather (周六 2026-09-19 is the 4th row, so days must be >= 5) and the exhibition from web search.

## Reference solution
1. get_weather {"location": "成都", "days": 5}
2. web_search 成都 展览 九月
Final answer: 周六晴、18~28°C，周日有阵雨（降水概率 55%）；成都博物馆正在办「锦官城外——蜀锦千年」特展（到 11 月 30 日，周一闭馆），周日下雨正好看展、周六适合去青城山。

## Why the answer is unique
Weekend dates follow the fixed clock; one exhibition is listed.

## Five alternative phrasings of the task
1. 成都周末天气怎么样？顺便看看有什么展
2. 这周末成都会下雨吗，有没有好看的展览
3. 周末在成都，天气和展览信息帮我查一下
4. 成都这周六周日天气，加上最近的展览
5. Chengdu this weekend: weather and any exhibitions?
