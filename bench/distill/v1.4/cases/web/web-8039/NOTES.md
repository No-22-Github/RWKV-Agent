## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.zhihu-like.cn/q/library-rules）给出 ，与官方页不一致；官方页（https://www.yungang-lib.cn/rules/borrow，2026-09-01）给出 45。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.yungang-lib.cn/rules/borrow，读出 45。
终答示例：普通图书借期 45 天（可续借一次 21 天），依据是云港市图书馆官网 2026 年 9 月 1 日修订的借阅规则；2024 年的攻略写的是旧规定。

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 45 才是答案， 是被取代 / 转述错误的值。官网借阅规则 2026-09-01 修订，攻略是 2024 年的整理。

## Five alternative phrasings of the task
1. 云港市图书馆普通图书借期
2. 云港市图书馆借书能借多久
3. 云港市图书馆借阅期限 普通图书 几天
4. 在云港市图书馆借一本书要几天内还
5. 云港市图书馆借阅规则 借期
