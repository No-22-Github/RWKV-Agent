## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://integrationguide.example.com/wicket）给出 100 requests / 1000 requests，与官方页不一致；官方页（https://wicket.example/docs/api/limits，2026-09-12）给出 60。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://wicket.example/docs/api/limits，读出 60。
终答示例：The free tier is limited to 60 requests per minute since the 1 September 2026 change (it was 30 before), according to Wicket's rate-limit docs; the integration guide's 100 is wrong or outdated.

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 60 才是答案，100 requests / 1000 requests 是被取代 / 转述错误的值。The official limits page is dated 2026-09-12 and lists the current tiers.

## Five alternative phrasings of the task
1. Wicket API free tier rate limit
2. Wicket free tier requests per minute
3. How many API calls per minute does Wicket allow on the free plan?
4. Wicket API rate limits free
5. Wicket free plan rate limit default
