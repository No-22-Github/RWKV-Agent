## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.railforum.example.net/t/northmoor-youth）给出 ，与官方页不一致；官方页（https://www.northmoorrail.example/passes/youth，2025-12-12）给出 27。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.northmoorrail.example/passes/youth，读出 27。
终答示例：The Youth Pass is open to people aged 16 to 27 inclusive since 1 January 2026, per Northmoor Rail's Youth Pass page. Older forum and savings-site pages cite lower age limits.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 27 才是答案， 是被取代 / 转述错误的值。The operator's page records the age band change effective 2026-01-01.

## Five alternative phrasings of the task
1. Northmoor Rail youth pass age limit
2. Northmoor Rail Youth Pass maximum age
3. How old can you be to get the Northmoor Rail youth pass?
4. Northmoor Rail Youth Pass eligibility age
5. Northmoor Rail youth pass upper age
