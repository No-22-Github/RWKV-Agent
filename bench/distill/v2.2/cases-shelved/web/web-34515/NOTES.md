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
12235
(fixture: qingchuan-trip.example/guide/lanyu-island-5days=5785)


## Five alternative phrasings of the task
1. 我想去兰屿岛玩五天，这是一篇攻略 https://qingchuan-trip.example/guide/lanyu-island-5days ，帮我整理一份行程要点：怎么去、住哪、玩什么、要花多少钱。
2. 麻烦帮我：我想去兰屿岛玩五天，这是一篇攻略 https://qingchuan-trip.example/guide/lanyu-island-5days ，帮我整理一份行程要点：怎么去、住哪、玩什么、要花多少钱。
3. 我想去兰屿岛玩五天，这是一篇攻略 https://qingchuan-trip.example/guide/lanyu-island-5days ，帮我整理一份行程要点：怎么去、住哪、玩什么、要花多少钱。（用中文回答）
4. 想请你看看：我想去兰屿岛玩五天，这是一篇攻略 https://qingchuan-trip.example/guide/lanyu-island-5days ，帮我整理一份行程要点：怎么去、住哪、玩什么、要花多少钱。
5. 再确认一下：我想去兰屿岛玩五天，这是一篇攻略 https://qingchuan-trip.example/guide/lanyu-island-5days ，帮我整理一份行程要点：怎么去、住哪、玩什么、要花多少钱。
