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
12756
(fixture: yuedong-watch.example/review/w3-pro-30days=6306)


## Five alternative phrasings of the task
1. 想买跃动 W3 Pro 手表，有篇评测 https://yuedong-watch.example/review/w3-pro-30days ，帮我看看续航、睡眠和价格的结论，最好说一下缺点。
2. 麻烦帮我：想买跃动 W3 Pro 手表，有篇评测 https://yuedong-watch.example/review/w3-pro-30days ，帮我看看续航、睡眠和价格的结论，最好说一下缺点。
3. 想买跃动 W3 Pro 手表，有篇评测 https://yuedong-watch.example/review/w3-pro-30days ，帮我看看续航、睡眠和价格的结论，最好说一下缺点。（用中文回答）
4. 想请你看看：想买跃动 W3 Pro 手表，有篇评测 https://yuedong-watch.example/review/w3-pro-30days ，帮我看看续航、睡眠和价格的结论，最好说一下缺点。
5. 再确认一下：想买跃动 W3 Pro 手表，有篇评测 https://yuedong-watch.example/review/w3-pro-30days ，帮我看看续航、睡眠和价格的结论，最好说一下缺点。
