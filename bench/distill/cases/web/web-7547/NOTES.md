## Traps
- TR-WEBSTALE: 排第一的是 2026-04-16 的旧博文，说 v1 自 API 版本 5 收紧；
  官方公告（2026-08-20）的 /v1/files/upload 行写明停用于 API 版本 6，
  且「弃用于 4」「停用于 6」两列并存，读错列会答 4（decoy 5 是旧博文的
  收紧版本号）。

## Reference solution
1. web_search 南栀云盘 接口变更公告（1）
2. web_fetch open.nanzhi.example/notices（2）
3. 读 /v1/files/upload 一行，答案 6（3）

## Why the answer is unique
官方公告的 /v1/files/upload 行给出唯一的停用版本：6；同行弃用于 4 是
另一列、另一件事，7 和 8 属于别的接口。旧博文的 5 是「开始收紧」的版本，
不是停用版本，且早于公告两个月，所以 6 是唯一站得住的答案。

## 正确答案
6

## Five alternative phrasings
1. 南栀云盘 v1 files upload 停用
2. 南栀开放平台 接口变更公告 upload
3. 南栀 v1 上传接口 第几版停用
4. 南栀云盘 接口停用时间表
5. 南栀 open notices v1 upload
