## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 race-memo.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
13778
(fixture: lakeside-run.example/event/2027-overview=5497, lakeside-run.example/event/registration-rules=3881)


## Five alternative phrasings of the task
1. 我想报名 2027 湖畔马拉松，帮我读赛事总览 https://lakeside-run.example/event/2027-overview 和报名规则，写个备忘到 race-memo.md，要有名额、关门时间、费用和退赛规则。
2. 麻烦帮我：我想报名 2027 湖畔马拉松，帮我读赛事总览 https://lakeside-run.example/event/2027-overview 和报名规则，写个备忘到 race-memo.md，要有名额、关门时间、费用和退赛规则。
3. 我想报名 2027 湖畔马拉松，帮我读赛事总览 https://lakeside-run.example/event/2027-overview 和报名规则，写个备忘到 race-memo.md，要有名额、关门时间、费用和退赛规则。（用中文回答）
4. 想请你看看：我想报名 2027 湖畔马拉松，帮我读赛事总览 https://lakeside-run.example/event/2027-overview 和报名规则，写个备忘到 race-memo.md，要有名额、关门时间、费用和退赛规则。
5. 再确认一下：我想报名 2027 湖畔马拉松，帮我读赛事总览 https://lakeside-run.example/event/2027-overview 和报名规则，写个备忘到 race-memo.md，要有名额、关门时间、费用和退赛规则。
