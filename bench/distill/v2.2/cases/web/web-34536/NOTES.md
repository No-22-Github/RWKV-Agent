## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 3 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
15664
(fixture: pulse-phone.example/p9/specs=3927, mall-shop.example/item/pulse-p9=4076, geekeval.example/reviews/pulse-p9=3311)


## Five alternative phrasings of the task
1. 我在看脉动 P9。官网规格 https://pulse-phone.example/p9/specs 、商城页 https://mall-shop.example/item/pulse-p9 、评测 https://geekeval.example/reviews/pulse-p9 都读一下，告诉我电池和快充官方数据与实测的差异，官方价和商城价各是多少，哪个页面的数据最权威。
2. 麻烦帮我：我在看脉动 P9。官网规格 https://pulse-phone.example/p9/specs 、商城页 https://mall-shop.example/item/pulse-p9 、评测 https://geekeval.example/reviews/pulse-p9 都读一下，告诉我电池和快充官方数据与实测的差异，官方价和商城价各是多少，哪个页面的数据最权威。
3. 我在看脉动 P9。官网规格 https://pulse-phone.example/p9/specs 、商城页 https://mall-shop.example/item/pulse-p9 、评测 https://geekeval.example/reviews/pulse-p9 都读一下，告诉我电池和快充官方数据与实测的差异，官方价和商城价各是多少，哪个页面的数据最权威。（用中文回答）
4. 想请你看看：我在看脉动 P9。官网规格 https://pulse-phone.example/p9/specs 、商城页 https://mall-shop.example/item/pulse-p9 、评测 https://geekeval.example/reviews/pulse-p9 都读一下，告诉我电池和快充官方数据与实测的差异，官方价和商城价各是多少，哪个页面的数据最权威。
5. 再确认一下：我在看脉动 P9。官网规格 https://pulse-phone.example/p9/specs 、商城页 https://mall-shop.example/item/pulse-p9 、评测 https://geekeval.example/reviews/pulse-p9 都读一下，告诉我电池和快充官方数据与实测的差异，官方价和商城价各是多少，哪个页面的数据最权威。
