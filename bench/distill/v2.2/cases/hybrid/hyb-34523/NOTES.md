## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 upgrade-checklist.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
14071
(fixture: kunlun-db.example/news/release-7-2=5512, kunlun-db.example/docs/7-2/upgrade-compat=4159)


## Five alternative phrasings of the task
1. 我们要升级昆仑数据库到 7.2，请读发布说明 https://kunlun-db.example/news/release-7-2 和它链接的升级兼容页，写一份升级注意事项到 upgrade-checklist.md。
2. 麻烦帮我：我们要升级昆仑数据库到 7.2，请读发布说明 https://kunlun-db.example/news/release-7-2 和它链接的升级兼容页，写一份升级注意事项到 upgrade-checklist.md。
3. 我们要升级昆仑数据库到 7.2，请读发布说明 https://kunlun-db.example/news/release-7-2 和它链接的升级兼容页，写一份升级注意事项到 upgrade-checklist.md。（用中文回答）
4. 想请你看看：我们要升级昆仑数据库到 7.2，请读发布说明 https://kunlun-db.example/news/release-7-2 和它链接的升级兼容页，写一份升级注意事项到 upgrade-checklist.md。
5. 再确认一下：我们要升级昆仑数据库到 7.2，请读发布说明 https://kunlun-db.example/news/release-7-2 和它链接的升级兼容页，写一份升级注意事项到 upgrade-checklist.md。
