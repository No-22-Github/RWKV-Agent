## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.coastwalkers.example.net/kestrel-point）给出 ，与官方页不一致；官方页（https://www.kestrelpoint.org/visit/tours，2026-09-01）给出 15:00。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.kestrelpoint.org/visit/tours，读出 15:00。
终答示例：The last weekend tour is at 15:00 (3 pm) on the winter timetable that started on 1 September, according to the lighthouse's own tours page. A July travel post describes the summer schedule.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 15:00 才是答案， 是被取代 / 转述错误的值。The official tours page was updated on 1 September for the winter timetable; the travel post describes the July summer schedule.

## Five alternative phrasings of the task
1. Kestrel Point lighthouse last tour weekend
2. Kestrel Point Lighthouse weekend tour times
3. When does the final guided tour start at Kestrel Point on a Saturday?
4. Kestrel Point Lighthouse Sunday last tour
5. Kestrel Point lighthouse tours opening hours weekends
