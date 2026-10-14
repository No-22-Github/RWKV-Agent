## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://baike.example-wiki.cn/yunti）给出 ，与官方页不一致；官方页（https://www.yunti-arena.cn/about/capacity，2026-07-05）给出 21500。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.yunti-arena.cn/about/capacity，读出 21500。
终答示例：演唱会模式最多容纳 21500 人（固定座席 18600 个），依据是云梯体育馆官网 2026 年 6 月改造后的场馆概况；百科是改造前的数据。

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 21500 才是答案， 是被取代 / 转述错误的值。官网概况更新于改造完成后，区分了固定座席与演唱会模式；百科和娱乐新闻用的是旧数或座席数。

## Five alternative phrasings of the task
1. 云梯体育馆演唱会最大容量
2. 云梯体育馆开演唱会能坐多少人
3. 云梯体育馆最多容纳观众 演唱会模式
4. 云梯体育馆容量
5. 云梯体育馆演唱会能进多少人
