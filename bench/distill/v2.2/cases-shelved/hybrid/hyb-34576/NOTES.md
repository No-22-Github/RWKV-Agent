## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 read_file/search_text 看 workers；turn2 web_fetch 长页面并跳到推荐值章节；turn3 replace_lines 改成推荐值；turn4 与第一轮的值比较

## Why the answer is unique
The edit target comes from the web page (turn 2); the last turn compares it with the value read in turn 1: 8 -> 24.

## Estimated trajectory tokens
10761
(fixture: gateway-guide.example/tuning/worker-threads=4789)


## Five alternative phrasings of the task
1. 部署文件夹里的订单网关配置，workers 现在设成多少？
2. 麻烦帮我：部署文件夹里的订单网关配置，workers 现在设成多少？
3. 部署文件夹里的订单网关配置，workers 现在设成多少？（用中文回答）
4. 想请你看看：部署文件夹里的订单网关配置，workers 现在设成多少？
5. 再确认一下：部署文件夹里的订单网关配置，workers 现在设成多少？
