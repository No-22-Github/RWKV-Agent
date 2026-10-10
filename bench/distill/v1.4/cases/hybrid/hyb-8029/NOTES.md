## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.dbaweekly.example.com/mallow-9-2）给出 ，与官方页不一致；官方页（https://mallowdb.example/support/lifecycle，2026-08-25）给出 2027-05-14。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://mallowdb.example/support/lifecycle，读出 2027-05-14。同时读本地文件取得对象信息（文件第一行就是决定对象的那一行）。
终答示例：The runbook shows we run Mallow DB 9.2, which reaches end of life on 14 May 2027 per the vendor's lifecycle page. A DBA newsletter's earlier date was for 9.1.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 2027-05-14 才是答案， 是被取代 / 转述错误的值。The runbook picks the series; the vendor lifecycle table gives dates per series.

## Five alternative phrasings of the task
1. When does the Mallow series in ops/runbook.yaml reach end of life?
2. ops/runbook.yaml Mallow version: what is the EOL date per Mallow?
3. Check the runbook's Mallow DB version, then find its end-of-life date on Mallow's site
4. Our Mallow DB version end of life date (see ops/runbook.yaml)
5. Mallow lifecycle: EOL for the release series we run in ops/runbook.yaml
