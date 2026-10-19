## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
作答。
第二轮追问同一页面的细节：search_text 在 .web 里搜或 read_file 跳读，再作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
12379
(fixture: harbormetrics.example/reports/2026-q3-shipping=5929)


## Five alternative phrasings of the task
1. Summarise https://harbormetrics.example/reports/2026-q3-shipping for me: the headline rate numbers, congestion, capacity and what they expect next.
2. 麻烦帮我：Summarise https://harbormetrics.example/reports/2026-q3-shipping for me: the headline rate numbers, congestion, capacity and what they expect next.
3. Summarise https://harbormetrics.example/reports/2026-q3-shipping for me: the headline rate numbers, congestion, capacity and what they expect next. (keep it organised)
4. 想请你看看：Summarise https://harbormetrics.example/reports/2026-q3-shipping for me: the headline rate numbers, congestion, capacity and what they expect next.
5. 再确认一下：Summarise https://harbormetrics.example/reports/2026-q3-shipping for me: the headline rate numbers, congestion, capacity and what they expect next.
