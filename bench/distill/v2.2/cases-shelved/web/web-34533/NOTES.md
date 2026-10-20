## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14049
(fixture: gov-qinghe.example/policy/housing-fund-2026=5073, news-qinghe.example/finance/housing-fund-explained=4826)


## Five alternative phrasings of the task
1. 青禾市公积金的新规，政府网站是 https://gov-qinghe.example/policy/housing-fund-2026 ，本地新闻的解读是 https://news-qinghe.example/finance/housing-fund-explained 。帮我对比两边，说清楚租房提取和贷款额度新旧各是多少，哪个是官方来源。
2. 麻烦帮我：青禾市公积金的新规，政府网站是 https://gov-qinghe.example/policy/housing-fund-2026 ，本地新闻的解读是 https://news-qinghe.example/finance/housing-fund-explained 。帮我对比两边，说清楚租房提取和贷款额度新旧各是多少，哪个是官方来源。
3. 青禾市公积金的新规，政府网站是 https://gov-qinghe.example/policy/housing-fund-2026 ，本地新闻的解读是 https://news-qinghe.example/finance/housing-fund-explained 。帮我对比两边，说清楚租房提取和贷款额度新旧各是多少，哪个是官方来源。（用中文回答）
4. 想请你看看：青禾市公积金的新规，政府网站是 https://gov-qinghe.example/policy/housing-fund-2026 ，本地新闻的解读是 https://news-qinghe.example/finance/housing-fund-explained 。帮我对比两边，说清楚租房提取和贷款额度新旧各是多少，哪个是官方来源。
5. 再确认一下：青禾市公积金的新规，政府网站是 https://gov-qinghe.example/policy/housing-fund-2026 ，本地新闻的解读是 https://news-qinghe.example/finance/housing-fund-explained 。帮我对比两边，说清楚租房提取和贷款额度新旧各是多少，哪个是官方来源。
