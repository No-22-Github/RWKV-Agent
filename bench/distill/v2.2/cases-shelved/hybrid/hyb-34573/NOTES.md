## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 web_fetch A（长页面）并跳到月费章节；turn2 同样处理 B；turn3 回到两个存档读开通费（search_text .web）；turn4 算 12 个月总价并 write_file

## Why the answer is unique
The last turn needs both monthly fees from turns 1 and 2 plus the setup fees: totals 4280 and 4380, so 拾码 is cheaper.

## Estimated trajectory tokens
14751
(fixture: shima-dev.example/pricing/team=4087, fengqiao-code.example/plans=4038)


## Five alternative phrasings of the task
1. 团队想选代码托管。先看拾码 https://shima-dev.example/pricing/team ，团队版（20 人）每月多少钱？
2. 麻烦帮我：团队想选代码托管。先看拾码 https://shima-dev.example/pricing/team ，团队版（20 人）每月多少钱？
3. 团队想选代码托管。先看拾码 https://shima-dev.example/pricing/team ，团队版（20 人）每月多少钱？（用中文回答）
4. 想请你看看：团队想选代码托管。先看拾码 https://shima-dev.example/pricing/team ，团队版（20 人）每月多少钱？
5. 再确认一下：团队想选代码托管。先看拾码 https://shima-dev.example/pricing/team ，团队版（20 人）每月多少钱？
