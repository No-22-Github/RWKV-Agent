## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 recall-note.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
9297
(fixture: jinsui-food.example/notice/recall-2026-10=5447)


## Five alternative phrasings of the task
1. 有个花生酱召回公告 https://jinsui-food.example/notice/recall-2026-10 ，我家好像买过。帮我写个简短说明存到 recall-note.md，列出涉及的批号、怎么退款、截止时间。
2. 麻烦帮我：有个花生酱召回公告 https://jinsui-food.example/notice/recall-2026-10 ，我家好像买过。帮我写个简短说明存到 recall-note.md，列出涉及的批号、怎么退款、截止时间。
3. 有个花生酱召回公告 https://jinsui-food.example/notice/recall-2026-10 ，我家好像买过。帮我写个简短说明存到 recall-note.md，列出涉及的批号、怎么退款、截止时间。（用中文回答）
4. 想请你看看：有个花生酱召回公告 https://jinsui-food.example/notice/recall-2026-10 ，我家好像买过。帮我写个简短说明存到 recall-note.md，列出涉及的批号、怎么退款、截止时间。
5. 再确认一下：有个花生酱召回公告 https://jinsui-food.example/notice/recall-2026-10 ，我家好像买过。帮我写个简短说明存到 recall-note.md，列出涉及的批号、怎么退款、截止时间。
