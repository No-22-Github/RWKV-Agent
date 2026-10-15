## Traps
- TR-FETCHFAIL: 搜索第一条链接打开失败（returns a 404 Not Found body），第二条文档页才有答案 45。放弃会答 UNKNOWN。
## Reference solution
1. web_search nimbusq client request timeout（1）
2. web_fetch 第一条，失败（2）
3. web_fetch 第二条，读到 45（3）。ref_calls=3。
## Why the answer is unique
只有第二条页面写了该默认值；第一条失败页与第三条（如有）不含数值。
## Five alternative phrasings of the task
1. nimbusq client request timeout default value
2. nimbusq client request timeout documentation default
3. nimbusq client request timeout configuration reference
4. nimbusq client request timeout client defaults
5. nimbusq client request timeout setting default number

## Prompt history
v1 题面写了「项目里没写过这个值」，DeepSeek 只搜工作区、从不调用 web_search（空工作区 + local-first 系统提示的已知偏置，见 web-0003 NOTES），r1 失败。去掉该句、改成「帮我查一下 / 它的文档在网上」这类用户口吻后 r2 通过。同时试过「想按文档里写的来」，仍不上网，无效。

EXAM-CANARY-1c8f3a96
