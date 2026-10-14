# log-7256 出题说明

## Traps
- TR-NEARNAME: 值班记录里写的 callback-0915.log 实际叫 pay-callback-0915.log（9 月起统一加前缀，见渠道值班.md）；照字面找不到文件，而 pay-callback-0914.log 是唯一形近的干扰文件，它里面第一条 ERROR 来自「渠道-淮海」。
- TR-DECOY: pay-callback-0915.log 里 10:02:11 有一条显眼的「[渠道-苏商] 回调响应超时 将重试」，它是 WARN 不是 ERROR，先读到它会把渠道答成「渠道-苏商」。

## Reference solution
1. 按渠道值班.md 的命名说明，把 callback-0915.log 对应到 pay-callback-0915.log（pay-callback-0914.log 是前一天的日志）。
2. 读 pay-callback-0915.log，跳过 10:02:11 的 WARN，第一条 ERROR 是 10:02:47 的「[渠道-金运] 回调签名校验失败」。
3. 对照 pay-callback-0914.log 确认其第一条 ERROR（渠道-淮海）属于 9 月 14 日，不在题面范围内。

## Why the answer is unique
题面要的是 9 月 15 日的回调日志：唯一日期匹配的文件是 pay-callback-0915.log（渠道值班.md 写明 9 月起都带 pay- 前缀，不存在第二个 0915 候选）。该文件里 10:02:11 那条是 WARN 级别，题面只要 ERROR，于是第一条 ERROR 唯一地是 10:02:47 的渠道-金运。「渠道-淮海」只在前一天文件的第一条 ERROR 里出现，「渠道-苏商」的 ERROR（10:14:08）晚于答案，两个诱饵都站不住。
