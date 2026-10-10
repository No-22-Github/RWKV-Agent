## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.lcdaily.cn/news/2026/electricity-tier）给出 ，与官方页不一致；官方页（https://www.lanchengpower.cn/tariff/residential，2026-07-01）给出 261。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.lanchengpower.cn/tariff/residential，读出 261。
终答示例：第二档从每月 261 度起算（261—420 度），依据是岚城供电 2026 年 7 月 1 日起执行的官方标准；去年底的新闻报道用的是旧口径。

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 261 才是答案， 是被取代 / 转述错误的值。官方标准 2026-07-01 起执行并给出区间，新闻稿是去年 12 月的旧口径。

## Five alternative phrasings of the task
1. 岚城阶梯电价第二档起点
2. 岚城居民用电 第二档 多少度起
3. 岚城供电阶梯电价 一档二档分界
4. 岚城每月用多少度电就进第二档？
5. 岚城电价阶梯现行标准
