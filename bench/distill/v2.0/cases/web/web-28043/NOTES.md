## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.wangdian-help.cn/xunda）给出 ，与官方页不一致；官方页（https://www.xunda-express.cn/price/surcharge，2026-07-28）给出 25。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.xunda-express.cn/price/surcharge，读出 25。
终答示例：单件超过 25 公斤起按大件收附加费（12 元/件），依据是迅达快递官网 8 月 1 日生效的附加费说明；网点整理的是旧标准。

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 25 才是答案， 是被取代 / 转述错误的值。官网附加费说明有生效日期 2026-08-01，网点整理是 2025 年的旧表。

## Five alternative phrasings of the task
1. 迅达快递大件附加费起收重量
2. 迅达快递 单件多重算大件
3. 迅达快递超过多少公斤要加收附加费
4. 迅达快递大件规定 公斤
5. 迅达快递附加费标准
