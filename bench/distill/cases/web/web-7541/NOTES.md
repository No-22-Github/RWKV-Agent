## Traps
- TR-SNIPPETVAGUE: 排第一的公告页摘要只说「时间表与迁移说明」，不含任何
  版本号，必须打开正文读 /v1/transfers 那一行；迁移指南（排第二）只给了
  「deprecated since API version 8」，直接拿它会答 8。

## Reference solution
1. web_search otterwick payments deprecation schedule (1)
2. web_fetch developers.otterwick.example/deprecations (2)
3. Read the /v1/transfers row and answer 14 (3)

## Why the answer is unique
The schedule's /v1/transfers row reads "removed in API version 14"; 13 and 15
belong to /v1/payouts.raw and /v1/refs. The migration guide's 8 is the
deprecated-since version, not a removal version, so 14 is the only number the
vendor page gives as the removal point for /v1/transfers.

## 正确答案
14

## Five alternative phrasings
1. otterwick payments deprecation schedule transfers
2. otterwick v1 transfers removed version
3. which api version removes otterwick transfers
4. otterwick payments legacy endpoint sunset
5. otterwick developers deprecations v1 transfers
