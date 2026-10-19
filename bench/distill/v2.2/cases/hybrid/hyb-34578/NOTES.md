## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 read_file/search_text 看 workers；turn2 web_fetch 长页面并跳到推荐值章节；turn3 replace_lines 改成推荐值；turn4 与第一轮的值比较

## Why the answer is unique
The edit target comes from the web page (turn 2); the last turn compares it with the value read in turn 1: 5 -> 20.

## Estimated trajectory tokens
10777
(fixture: mq-practice.example/consumer-scaling=4903)


## Five alternative phrasings of the task
1. 运维文件夹的队列消费者配置里，现在 workers 是几？
2. 麻烦帮我：运维文件夹的队列消费者配置里，现在 workers 是几？
3. 运维文件夹的队列消费者配置里，现在 workers 是几？（用中文回答）
4. 想请你看看：运维文件夹的队列消费者配置里，现在 workers 是几？
5. 再确认一下：运维文件夹的队列消费者配置里，现在 workers 是几？
