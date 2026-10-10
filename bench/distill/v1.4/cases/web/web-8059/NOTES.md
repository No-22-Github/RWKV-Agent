## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.pyweekly.example.com/ferrule-3）给出 ，与官方页不一致；官方页（https://ferrule.example/docs/install，2026-08-19）给出 3.10。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://ferrule.example/docs/install，读出 3.10。
终答示例：Ferrule 4.0 needs Python 3.10 or newer; 3.8 and 3.9 were dropped in 4.0 according to the official install docs. An older tutorial still lists older Pythons.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 3.10 才是答案， 是被取代 / 转述错误的值。The 4.0 install doc is explicit; the tutorial describes the 3.x series.

## Five alternative phrasings of the task
1. Ferrule 4.0 minimum Python version
2. Ferrule 4.0 requirements Python
3. Which Python do I need for Ferrule 4.0?
4. Ferrule 4.0 supported Python versions minimum
5. Ferrule 4.0 install requirements
