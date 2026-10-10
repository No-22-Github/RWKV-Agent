## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.ridertests.example.com/orbit-ridge-s2）给出 ，与官方页不一致；官方页（https://www.orbitridge.example/s2/specs，2026-05-12）给出 55。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.orbitridge.example/s2/specs，读出 55。
终答示例：The official claimed range is 55 km (75 kg rider, 20 km/h, flat road), from Orbit Ridge's S2 spec page. The review quotes a pre-release sheet.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 55 才是答案， 是被取代 / 转述错误的值。The manufacturer's spec page is the primary source and postdates the review's pre-release number.

## Five alternative phrasings of the task
1. Orbit Ridge S2 range
2. Orbit Ridge S2 electric scooter claimed range km
3. How far can the Orbit Ridge S2 go on a charge according to the maker?
4. Orbit Ridge S2 specs range
5. Orbit Ridge S2 official range
