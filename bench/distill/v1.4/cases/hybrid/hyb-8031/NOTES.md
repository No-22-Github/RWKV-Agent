## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.eventplanner.example.com/quayside）给出 280 theatre / 280 people / 280 seats / 280 guests，与官方页不一致；官方页（https://www.quaysidecentre.example/halls，2026-07-11）给出 340。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.quaysidecentre.example/halls，读出 340。同时读本地文件取得对象信息（文件第一行就是决定对象的那一行）。
终答示例：The notes shortlist Cedar Hall; the venue's own halls page (updated after the refurbishment on 2026-07-11) gives 340 in theatre layout. A directory profile still lists the old 280.

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 340 才是答案，280 theatre / 280 people / 280 seats / 280 guests 是被取代 / 转述错误的值。The notes pick the hall; the venue page is newer and post-refurbishment.

## Five alternative phrasings of the task
1. Theatre-layout capacity of the shortlisted Quayside Centre hall in venue/hire-notes.txt
2. Look up the shortlisted hall at Quayside Centre and how many it seats theatre style
3. venue/hire-notes.txt has the hall; what's its theatre capacity on the Quayside Centre website?
4. How many delegates does our shortlisted Quayside Centre hall seat in theatre layout?
5. Quayside Centre: theatre seating for the hall in our hire notes
