## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.caijing-baodian.cn/a/gjj-binjiang）给出 ，与官方页不一致；官方页（https://gjj.binjiang.gov.cn/notice/2026-base，2026-06-20）给出 31200。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://gjj.binjiang.gov.cn/notice/2026-base，读出 31200。
终答示例：月缴存基数上限现为 31200 元（下限 2690 元），依据是滨江市公积金中心 2026 年度调整通知，7 月 1 日起执行；财经号引用的是上一年度数值。

## Changelog
- v2：S5：query_match 由「滨江市住房公积金」缩为「滨江」——老师的搜索词把城市和「住房公积金」分开写，三遍搜索全部零结果；另去掉旧值排除项（同上）。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 31200 才是答案， 是被取代 / 转述错误的值。政府通知给出 2026-07-01 起的新基数，财经号引用的是上一年度通知。

## Five alternative phrasings of the task
1. 滨江市住房公积金缴存基数上限
2. 滨江市公积金月缴存基数最高多少
3. 滨江市公积金基数上限 2026
4. 滨江市住房公积金每月最高按多少基数缴
5. 滨江公积金缴存基数 上限 现行
