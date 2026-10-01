## Traps
- TR-EARLYHIT: 排第一的官方公告摘要已给出移除版本 16，摘要即可作答；
  expect.max_calls 只给一次搜索预算。旧博文（排第二）说的 12 是
  deprecated-since 版本（decoy 12）。

## Reference solution
1. web_search otterwick webhooks v1 retirement (1)
2. Answer 16 from the official notice snippet (2)

## Why the answer is unique
The vendor notice states /v1/webhooks will be removed in API version 16. The
blog's 12 marks when the endpoint was deprecated, not when it is removed, so
it is a different milestone rather than a defensible reading, and 16 is the
only removal version the vendor gives.

## 正确答案
16

## Five alternative phrasings
1. otterwick webhooks v1 retirement notice
2. otterwick v1 webhooks removed version
3. which api version removes otterwick webhooks
4. otterwick payments webhooks cutover
5. otterwick developers notices webhooks
