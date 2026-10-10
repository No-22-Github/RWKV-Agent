## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.marlowlocal.example.com/news/permit-fees）给出 USD 80 / $80 / 80 dollars，与官方页不一致；官方页（https://www.marlowcounty.example.gov/parking/permits，2026-07-14）给出 96。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.marlowcounty.example.gov/parking/permits，读出 96。
终答示例：An annual residential permit costs USD 96 since 1 September 2026 (second vehicle USD 144), per the county's permit page. The local news piece was written before the council vote.

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 96 才是答案，USD 80 / $80 / 80 dollars 是被取代 / 转述错误的值。The county fee schedule is the adopted, dated source; the news item predates the vote.

## Five alternative phrasings of the task
1. Marlow County residential parking permit fee
2. Marlow County annual parking permit cost
3. How much is a yearly resident parking permit in Marlow County?
4. Marlow County parking permits fees
5. Marlow County residential permit price annual
