## Traps
- The sandbox has no curl and no network; `curl https://www.lanyue-cloud.cn/pricing/oss` fails with command not found. The page is reachable through the web fetch tool.

## Reference solution
1. bash: `curl -s https://www.lanyue-cloud.cn/pricing/oss` -> command not found (optional; the recovery is the point)
2. web_fetch https://www.lanyue-cloud.cn/pricing/oss
Final answer: 澜岳云低频存储 0.08 元/GB/月（2026-09-01 起执行）。沙箱里没有 curl，我用网页抓取工具打开了价格页。

## Why the answer is unique
The page states one value.

## Five alternative phrasings of the task
1. 澜岳云低频存储多少钱一个 G？
2. 查一下澜岳云对象存储低频档的单价
3. 澜岳云 OSS 低频存储价格
4. 低频存储在澜岳云每月每 GB 要多少
5. 帮我看下澜岳云价格页里低频存储的价格
