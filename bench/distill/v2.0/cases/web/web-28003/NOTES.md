## Traps
- TR-WEBSTALE: 搜索结果第一条是 2025 年 11 月的博客，说默认 48 小时；官方 4.x 文档（2026-07-14 更新）写明 4.0 起默认值从 48 提到 72 小时。

## Reference solution
1. 搜索 Quarrel 4.x 消息保留：两条结果，博客和官方文档。
2. 抓取官方文档 https://quarrelmq.io/docs/4.x/retention：retention.hours 默认 72。
终答 1–2 句：4.x 默认保留 72 小时，依据是官方 4.x 文档；网上一些旧文章写的是 4.0 之前的默认值，已经不适用。判据：包含 72（独立词元），不出现「48 小时」，抓取过页面。

## Why the answer is unique
题面限定 4.x，官方文档明确 4.0 起改为 72；博客早于此且不是官方来源。

## Five alternative phrasings of the task
1. Quarrel 4.x 消息保留时长 默认
2. quarrel retention hours default
3. Quarrel 消息队列 默认保留
4. quarrel 4.x retention.hours
5. Quarrel MQ 消息保留多久
