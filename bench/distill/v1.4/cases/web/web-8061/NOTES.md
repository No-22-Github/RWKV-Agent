## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://dbtips.example.net/sorrel-tuning）给出 is 100 / default 100 / default is 100 / 100 connections / defaults to 100，与官方页不一致；官方页（https://sorrel-db.example/docs/3.x/settings，2026-08-08）给出 400。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://sorrel-db.example/docs/3.x/settings，读出 400。
终答示例：In Sorrel 3.x max_connections defaults to 400 (raised from 100 in 3.0), per the official settings reference; older tuning tips still quote 100.

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 400 才是答案，is 100 / default 100 / default is 100 / 100 connections / defaults to 100 是被取代 / 转述错误的值。The 3.x reference documents the changed default.

## Five alternative phrasings of the task
1. Sorrel 3.x default max_connections
2. Sorrel max_connections default value
3. How many connections does Sorrel 3 allow by default?
4. Sorrel 3.x settings max_connections
5. Sorrel database max_connections 3.x default
