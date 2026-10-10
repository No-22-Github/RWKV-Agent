## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.walkingholidays.example.com/hollin-gorge）给出 ，与官方页不一致；官方页（https://www.hollingorge.example.org/visit/fees，2026-03-20）给出 7.50。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.hollingorge.example.org/visit/fees，读出 7.50。
终答示例：Adult entry is GBP 7.50 from 1 April 2026 (children 5-15 GBP 3.50), per the reserve's fees page; a 2025 walking guide lists a lower fee.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 7.50 才是答案， 是被取代 / 转述错误的值。The reserve's fees page gives the April 2026 prices; the guide is from 2025.

## Five alternative phrasings of the task
1. Hollin Gorge nature reserve adult entry fee
2. Hollin Gorge adult admission price
3. How much does an adult pay to get into Hollin Gorge?
4. Hollin Gorge reserve fees adult
5. Hollin Gorge nature reserve entry price adult
