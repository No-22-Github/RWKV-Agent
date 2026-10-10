## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.saascompare.example.com/quartzly）给出 ，与官方页不一致；官方页（https://quartzly.example/pricing，2026-09-08）给出 14。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://quartzly.example/pricing，读出 14。同时读本地文件取得对象信息（文件第一行就是决定对象的那一行）。
终答示例：We're on the Business plan, which the vendor's pricing page (updated 2026-09-08) lists at USD 14 per seat per month, up since the end of August. A comparison site still shows the old figure.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 14 才是答案， 是被取代 / 转述错误的值。The vendor notes name the plan; the vendor's pricing page is current and states the price change date.

## Five alternative phrasings of the task
1. Which Quartzly plan are we on (docs/vendor-notes.txt) and what does it cost per seat today?
2. Look at docs/vendor-notes.txt for our Quartzly plan, then get the current per-seat price from Quartzly
3. Quartzly: current monthly per-seat price for the plan in our vendor notes
4. What's our Quartzly plan's per-seat monthly price right now, per the vendor?
5. From docs/vendor-notes.txt find the Quartzly tier, then check Quartzly's pricing page
