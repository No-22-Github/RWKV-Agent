## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 web_fetch A（长页面）并跳到月费章节；turn2 同样处理 B；turn3 回到两个存档读开通费（search_text .web）；turn4 算 12 个月总价并 write_file

## Why the answer is unique
The last turn needs both monthly fees from turns 1 and 2 plus the setup fees: totals 6060 and 6000, so 澜海数据 is cheaper.

## Estimated trajectory tokens
14728
(fixture: yunyan-hosting.example/plans/colocation=3905, lanhai-idc.example/price/rack-1u=4179)


## Five alternative phrasings of the task
1. 我们想把一台服务器托管出去，先看云砚托管的页面 https://yunyan-hosting.example/plans/colocation ，标准 1U 托管套餐每月多少钱？
2. 麻烦帮我：我们想把一台服务器托管出去，先看云砚托管的页面 https://yunyan-hosting.example/plans/colocation ，标准 1U 托管套餐每月多少钱？
3. 我们想把一台服务器托管出去，先看云砚托管的页面 https://yunyan-hosting.example/plans/colocation ，标准 1U 托管套餐每月多少钱？（用中文回答）
4. 想请你看看：我们想把一台服务器托管出去，先看云砚托管的页面 https://yunyan-hosting.example/plans/colocation ，标准 1U 托管套餐每月多少钱？
5. 再确认一下：我们想把一台服务器托管出去，先看云砚托管的页面 https://yunyan-hosting.example/plans/colocation ，标准 1U 托管套餐每月多少钱？
