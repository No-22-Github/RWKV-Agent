## Traps
- TR-SNIPPETVAGUE: 排第一的产品页摘要只说「自有发布线」，不含版本号；
  必须打开 changelog 正文。changelog 末尾顺手提到的 3.14.2 是 PDF toolkit
  的版本（decoy），属于相邻产品的相近键值。

## Reference solution
1. web_search fernwave convert cli changelog (1)
2. web_fetch docs.fernwave.example/convert-changelog (2)
3. Answer 1.9.7 (3)

## Why the answer is unique
Convert CLI 的 changelog 只标了一个 current stable：1.9.7（2026-08-21）。
末尾提到的 3.14.2 明确属于「另一个产品」PDF toolkit，且页面标题与章节都
是 Convert 自己的发布线，所以 1.9.7 是唯一可以写进构建服务器的版本号。

## 正确答案
1.9.7

## Five alternative phrasings
1. fernwave convert cli changelog
2. fernwave convert current stable version
3. which fernwave convert version is stable
4. fernwave convert cli release history
5. fernwave convert version for build server
