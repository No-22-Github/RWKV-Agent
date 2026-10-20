## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14545
(fixture: rivergo-db.example/docs/release/2-6=5259, pinesql.example/docs/release/9-1=5136)


## Five alternative phrasings of the task
1. 我们要选数据库，河马数据库 2.6 发布说明在 https://rivergo-db.example/docs/release/2-6 ，松针数据库 9.1 在 https://pinesql.example/docs/release/9-1 。对比维护期、内核要求、写入吞吐和许可证，哪个发布更晚？
2. 麻烦帮我：我们要选数据库，河马数据库 2.6 发布说明在 https://rivergo-db.example/docs/release/2-6 ，松针数据库 9.1 在 https://pinesql.example/docs/release/9-1 。对比维护期、内核要求、写入吞吐和许可证，哪个发布更晚？
3. 我们要选数据库，河马数据库 2.6 发布说明在 https://rivergo-db.example/docs/release/2-6 ，松针数据库 9.1 在 https://pinesql.example/docs/release/9-1 。对比维护期、内核要求、写入吞吐和许可证，哪个发布更晚？（用中文回答）
4. 想请你看看：我们要选数据库，河马数据库 2.6 发布说明在 https://rivergo-db.example/docs/release/2-6 ，松针数据库 9.1 在 https://pinesql.example/docs/release/9-1 。对比维护期、内核要求、写入吞吐和许可证，哪个发布更晚？
5. 再确认一下：我们要选数据库，河马数据库 2.6 发布说明在 https://rivergo-db.example/docs/release/2-6 ，松针数据库 9.1 在 https://pinesql.example/docs/release/9-1 。对比维护期、内核要求、写入吞吐和许可证，哪个发布更晚？
