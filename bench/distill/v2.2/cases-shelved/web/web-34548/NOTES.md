## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
web_search -> 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14369
(fixture: langwan-hotel.example/booking/terms=5124, haiyu-hotel.example/policy=5095)


## Five alternative phrasings of the task
1. 我们打算在岚湾酒店和海屿酒店里选一家，帮我搜一下这两家的预订条款，比较入住退房时间、取消政策、押金和早餐。
2. 麻烦帮我：我们打算在岚湾酒店和海屿酒店里选一家，帮我搜一下这两家的预订条款，比较入住退房时间、取消政策、押金和早餐。
3. 我们打算在岚湾酒店和海屿酒店里选一家，帮我搜一下这两家的预订条款，比较入住退房时间、取消政策、押金和早餐。（用中文回答）
4. 想请你看看：我们打算在岚湾酒店和海屿酒店里选一家，帮我搜一下这两家的预订条款，比较入住退房时间、取消政策、押金和早餐。
5. 再确认一下：我们打算在岚湾酒店和海屿酒店里选一家，帮我搜一下这两家的预订条款，比较入住退房时间、取消政策、押金和早餐。
