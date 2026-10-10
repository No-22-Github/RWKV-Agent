## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://tieba.example-forum.cn/p/ludao-ferry）给出 ，与官方页不一致；官方页（https://www.ludao-ferry.cn/fares，2026-08-10）给出 22。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.ludao-ferry.cn/fares，读出 22。
终答示例：成人单程票价 22 元（儿童 11 元），依据是鹭岛轮渡官网 2026 年 8 月 15 日起执行的票价公告；论坛和百科里的价格是旧数据。

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 22 才是答案， 是被取代 / 转述错误的值。官方公告给出自 2026-08-15 起的现行价，论坛和百科是 2024、2025 年的数据。

## Five alternative phrasings of the task
1. 鹭岛轮渡成人票价
2. 鹭岛轮渡单程多少钱 大人
3. 坐鹭岛轮渡一个大人要多少钱
4. 鹭岛轮渡现行票价 成人 单程
5. 鹭岛轮渡船票现在什么价
