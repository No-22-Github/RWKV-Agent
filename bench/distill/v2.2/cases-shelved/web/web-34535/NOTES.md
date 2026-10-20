## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
12929
(fixture: zhixing-tickets.example/notice/spring-festival-2027=5436, travelbbs-wang.example/t/spring-festival-tips=3343)


## Five alternative phrasings of the task
1. 我要买 2027 年春节的火车票。看了铁路客服中心的通知 https://zhixing-tickets.example/notice/spring-festival-2027 和论坛经验帖 https://travelbbs-wang.example/t/spring-festival-tips ，两边预售期和候补时间不一样。帮我理一下今年到底是多少天预售、候补什么时候截止、退票怎么收费，以及为什么论坛帖不能直接参考。
2. 麻烦帮我：我要买 2027 年春节的火车票。看了铁路客服中心的通知 https://zhixing-tickets.example/notice/spring-festival-2027 和论坛经验帖 https://travelbbs-wang.example/t/spring-festival-tips ，两边预售期和候补时间不一样。帮我理一下今年到底是多少天预售、候补什么时候截止、退票怎么收费，以及为什么论坛帖不能直接参考。
3. 我要买 2027 年春节的火车票。看了铁路客服中心的通知 https://zhixing-tickets.example/notice/spring-festival-2027 和论坛经验帖 https://travelbbs-wang.example/t/spring-festival-tips ，两边预售期和候补时间不一样。帮我理一下今年到底是多少天预售、候补什么时候截止、退票怎么收费，以及为什么论坛帖不能直接参考。（用中文回答）
4. 想请你看看：我要买 2027 年春节的火车票。看了铁路客服中心的通知 https://zhixing-tickets.example/notice/spring-festival-2027 和论坛经验帖 https://travelbbs-wang.example/t/spring-festival-tips ，两边预售期和候补时间不一样。帮我理一下今年到底是多少天预售、候补什么时候截止、退票怎么收费，以及为什么论坛帖不能直接参考。
5. 再确认一下：我要买 2027 年春节的火车票。看了铁路客服中心的通知 https://zhixing-tickets.example/notice/spring-festival-2027 和论坛经验帖 https://travelbbs-wang.example/t/spring-festival-tips ，两边预售期和候补时间不一样。帮我理一下今年到底是多少天预售、候补什么时候截止、退票怎么收费，以及为什么论坛帖不能直接参考。
