## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 read_file/search_text 看 workers；turn2 web_fetch 长页面并跳到推荐值章节；turn3 replace_lines 改成推荐值；turn4 与第一轮的值比较

## Why the answer is unique
The edit target comes from the web page (turn 2); the last turn compares it with the value read in turn 1: 6 -> 18.

## Estimated trajectory tokens
10587
(fixture: billingtools.example/docs/scaling-workers=4637)


## Five alternative phrasings of the task
1. In deploy/billing-worker.yaml, what is workers set to right now?
2. 麻烦帮我：In deploy/billing-worker.yaml, what is workers set to right now?
3. In deploy/billing-worker.yaml, what is workers set to right now? (keep it organised)
4. 想请你看看：In deploy/billing-worker.yaml, what is workers set to right now?
5. 再确认一下：In deploy/billing-worker.yaml, what is workers set to right now?
