## Traps
- The sandbox has no curl and no network; `curl https://open.qinghe-api.cn/docs/ratelimit` fails with command not found. The page is reachable through the web fetch tool.

## Reference solution
1. bash: `curl -s https://open.qinghe-api.cn/docs/ratelimit` -> command not found (optional; the recovery is the point)
2. web_fetch https://open.qinghe-api.cn/docs/ratelimit
Final answer: 青禾开放平台默认每个应用每分钟 600 次，超出返回 429（企业版可提到 3000 次）。沙箱没有 curl，我用网页抓取工具读的文档。

## Why the answer is unique
The page states one value.

## Five alternative phrasings of the task
1. 青禾开放平台默认限流是多少？
2. 青禾接口每分钟能调多少次
3. 查一下青禾 API 的默认频率限制
4. 青禾平台超过多少次会 429
5. 青禾开放平台的限流文档里默认值是多少
