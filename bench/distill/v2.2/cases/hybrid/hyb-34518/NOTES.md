## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 price-notes.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
9524
(fixture: jifeng-express.example/notice/2026-winter-price=5674)


## Five alternative phrasings of the task
1. 疾风快递冬季涨价了，公告在 https://jifeng-express.example/notice/2026-winter-price ，帮我整理成一份给店员看的价格和时效要点，存到 price-notes.md。
2. 麻烦帮我：疾风快递冬季涨价了，公告在 https://jifeng-express.example/notice/2026-winter-price ，帮我整理成一份给店员看的价格和时效要点，存到 price-notes.md。
3. 疾风快递冬季涨价了，公告在 https://jifeng-express.example/notice/2026-winter-price ，帮我整理成一份给店员看的价格和时效要点，存到 price-notes.md。（用中文回答）
4. 想请你看看：疾风快递冬季涨价了，公告在 https://jifeng-express.example/notice/2026-winter-price ，帮我整理成一份给店员看的价格和时效要点，存到 price-notes.md。
5. 再确认一下：疾风快递冬季涨价了，公告在 https://jifeng-express.example/notice/2026-winter-price ，帮我整理成一份给店员看的价格和时效要点，存到 price-notes.md。
