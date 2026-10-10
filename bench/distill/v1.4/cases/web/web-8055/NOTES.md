## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.softwaredeals.example.com/plover-notes-review）给出 ，与官方页不一致；官方页（https://www.plovernotes.example/pricing，2026-09-03）给出 6。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.plovernotes.example/pricing，读出 6。
终答示例：Plover Notes Pro is USD 6 per month billed monthly (USD 60 per year), according to the vendor's pricing page updated 3 September 2026. The review's price is outdated.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 6 才是答案， 是被取代 / 转述错误的值。The vendor pricing page is current and dated; the review is from January.

## Five alternative phrasings of the task
1. Plover Notes Pro monthly price
2. Plover Notes Pro price per month
3. How much is Plover Notes Pro a month?
4. Plover Notes pricing Pro monthly
5. Plover Notes Pro plan cost monthly billing
