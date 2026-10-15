## Traps
- TR-FETCHFAIL: 搜索第一条链接打开失败（返回 404 页面），第二条文档页才有答案 5。放弃会答 UNKNOWN。
## Reference solution
1. web_search okapi-queue 默认重试次数（1）
2. web_fetch 第一条，失败（2）
3. web_fetch 第二条，读到 5（3）。ref_calls=3。
## Why the answer is unique
只有第二条页面写了该默认值；第一条失败页与第三条（如有）不含数值。
## Five alternative phrasings of the task
1. okapi-queue 默认重试次数 default value
2. okapi-queue 默认重试次数 documentation default
3. okapi-queue 默认重试次数 configuration reference
4. okapi-queue 默认重试次数 client defaults
5. okapi-queue 默认重试次数 setting default number

## Prompt history
v1 题面写了「项目里没写过这个值」，DeepSeek 只搜工作区、从不调用 web_search（空工作区 + local-first 系统提示的已知偏置，见 web-0003 NOTES），r1 失败。去掉该句、改成「帮我查一下 / 它的文档在网上」这类用户口吻后 r2 通过。同时试过「想按文档里写的来」，仍不上网，无效。

EXAM-CANARY-e6a02f5d
