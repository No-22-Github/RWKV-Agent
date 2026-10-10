## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.xiaoyou-travel.cn/notes/wangchao）给出 ，与官方页不一致；官方页（https://www.wangchao-museum.cn/visit，2026-09-05）给出 17:30。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.wangchao-museum.cn/visit，读出 17:30。
终答示例：周末（周二至周日）17:30 闭馆，17:00 后停止入馆，依据是望潮博物馆官网参观指南；夏季延时到 8 点的安排 8 月底就结束了。

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 17:30 才是答案， 是被取代 / 转述错误的值。官网参观指南更新于 9 月，写明夏季延时已结束；游记是 7 月的夏季安排。

## Five alternative phrasings of the task
1. 望潮博物馆周末闭馆时间
2. 望潮博物馆周六周日几点关门
3. 去望潮博物馆，周末最晚什么时候能进？几点闭馆
4. 望潮博物馆开放时间 周末
5. 望潮博物馆周末下午能逛到几点
