## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast from get_weather (后天 is the third row) and 长沙 张家界 高铁 最快时长 from web search; the weather part must not be searched.
- TR-DECOY: tomorrow is 多云; only 后天 (2026-09-18) is 中雨.

## Reference solution
1. get_weather {"location": "长沙", "days": 3}
2. web_search 长沙 张家界 高铁 最快时长
Final answer: 长沙南到张家界西最快约 1 小时 59 分；长沙后天（9 月 18 日）中雨，降水概率 80%，22~27°C，出发记得带伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value.

## Five alternative phrasings of the task
1. 查下长沙到张家界高铁最快用时，再告诉我长沙后天天气
2. 周五从长沙去张家界，高铁多久，那天长沙天气怎样
3. 长沙后天天气和去张家界高铁时长
4. 长沙—张家界高铁最短多长时间？后天天气呢
5. Changsha to Zhangjiajie high-speed train time, and Changsha's weather the day after tomorrow?
