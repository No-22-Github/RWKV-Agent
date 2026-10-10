## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.feixing-blog.cn/haiyan-baggage）给出 ，与官方页不一致；官方页（https://www.haiyan-air.cn/service/baggage，2026-09-10）给出 20。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.haiyan-air.cn/service/baggage，读出 20。
终答示例：国内航线经济舱可免费托运 20 公斤（国际 23 公斤），依据是海燕航空官网 9 月 15 日起适用的行李规定；博客写的是旧标准。

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 20 才是答案， 是被取代 / 转述错误的值。官网行李规定标明适用日期 2026-09-15，博客是 2025 年的攻略。

## Five alternative phrasings of the task
1. 海燕航空经济舱免费托运行李额
2. 海燕航空 经济舱 托运行李 多少公斤免费
3. 坐海燕航空经济舱，托运行李免费多重
4. 海燕航空国内航线行李额
5. 海燕航空托运行李规定 经济舱
