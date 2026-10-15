## Traps
- TR-FETCHFAIL: 搜索第一条链接打开失败（fetch error (HTTP 404) on the first link），第二条文档页才有答案 25。放弃会答 UNKNOWN。
## Reference solution
1. web_search quarryhub free plan upload size（1）
2. web_fetch 第一条，失败（2）
3. web_fetch 第二条，读到 25（3）。ref_calls=3。
## Why the answer is unique
只有第二条页面写了该默认值；第一条失败页与第三条（如有）不含数值。
## Five alternative phrasings of the task
1. quarryhub free plan upload size default value
2. quarryhub free plan upload size documentation default
3. quarryhub free plan upload size configuration reference
4. quarryhub free plan upload size client defaults
5. quarryhub free plan upload size setting default number

EXAM-CANARY-92d5b7e4
