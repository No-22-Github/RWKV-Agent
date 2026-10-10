## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://stackhelp.example.dev/q/gantry-dashboard-port）给出 ，与官方页不一致；官方页（https://gantry.example/docs/v2/config，2026-07-02）给出 7430。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://gantry.example/docs/v2/config，读出 7430。
终答示例：In Gantry v2 the dashboard listens on port 7430 by default, per the official v2 configuration docs. The v1 default was different.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 7430 才是答案， 是被取代 / 转述错误的值。The v2 configuration page states the new default and the old one explicitly.

## Five alternative phrasings of the task
1. Gantry v2 dashboard default port
2. Gantry dashboard.port default v2
3. Which port does the Gantry v2 dashboard use by default?
4. Gantry v2 configuration dashboard port
5. Gantry 2 dashboard port default
