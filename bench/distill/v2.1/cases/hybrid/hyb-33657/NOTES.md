## Traps
TR-MULTISRC

## Reference solution
1. list_files / read_file 出差/行程.md -> destination 苏州, departure 2026-09-18
2. get_weather 苏州 days>=3
Answer: 09-18 中雨, 75%. Decoys: the previous trip city 北京, today's 20%.

## Why the answer is unique
Recomputed from the fixture / fixed clock (2026-09-16 10:00 Asia/Shanghai). Expected: ["all", ["75%"]] 

## Five alternative phrasings of the task
1. 行程里的目的地出发当天天气如何
2. 我出发那天去的城市会下雨吗
3. 按出差行程查目的地出发日的天气
4. 出差文件夹行程中目的地，出发日天气预报
5. Check the destination weather on the departure day in my trip notes
