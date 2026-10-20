## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 web_fetch A（长页面）并跳到月费章节；turn2 同样处理 B；turn3 回到两个存档读开通费（search_text .web）；turn4 算 12 个月总价并 write_file

## Why the answer is unique
The last turn needs both monthly fees from turns 1 and 2 plus the setup fees: totals 5290 and 5220, so Marigold Services is cheaper.

## Estimated trajectory tokens
14364
(fixture: brightnest-clean.example/pricing=3867, marigold-services.example/office/rates=3899)


## Five alternative phrasings of the task
1. Let's price office cleaning. On BrightNest's page https://brightnest-clean.example/pricing , how much is the weekly office cleaning plan per month?
2. 麻烦帮我：Let's price office cleaning. On BrightNest's page https://brightnest-clean.example/pricing , how much is the weekly office cleaning plan per month?
3. Let's price office cleaning. On BrightNest's page https://brightnest-clean.example/pricing , how much is the weekly office cleaning plan per month? (keep it organised)
4. 想请你看看：Let's price office cleaning. On BrightNest's page https://brightnest-clean.example/pricing , how much is the weekly office cleaning plan per month?
5. 再确认一下：Let's price office cleaning. On BrightNest's page https://brightnest-clean.example/pricing , how much is the weekly office cleaning plan per month?
