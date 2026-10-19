## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 web_fetch A（长页面）并跳到月费章节；turn2 同样处理 B；turn3 回到两个存档读开通费（search_text .web）；turn4 算 12 个月总价并 write_file

## Why the answer is unique
The last turn needs both monthly fees from turns 1 and 2 plus the setup fees: totals 1940 and 1980, so Noteflow is cheaper.

## Estimated trajectory tokens
14431
(fixture: noteflow-app.example/plans/team=3861, pagewright.example/pricing/teams=3977)


## Five alternative phrasings of the task
1. We are choosing a notes tool for the team. On https://noteflow-app.example/plans/team , how much is the Team plan for 15 members per month?
2. 麻烦帮我：We are choosing a notes tool for the team. On https://noteflow-app.example/plans/team , how much is the Team plan for 15 members per month?
3. We are choosing a notes tool for the team. On https://noteflow-app.example/plans/team , how much is the Team plan for 15 members per month? (keep it organised)
4. 想请你看看：We are choosing a notes tool for the team. On https://noteflow-app.example/plans/team , how much is the Team plan for 15 members per month?
5. 再确认一下：We are choosing a notes tool for the team. On https://noteflow-app.example/plans/team , how much is the Team plan for 15 members per month?
