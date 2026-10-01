# log-7260 出题说明

## Traps
- （本题无声明陷阱，L0 基题：直接计数，日志里混有借书成功与打印机告警作普通噪声。）

## Reference solution
1. 读取 circulation.log，筛选消息含「扣款失败」的记录并计数，得 14 次。

## Why the answer is unique
「扣款失败」字样恰好出现在 14 条 ERROR 里；INFO 借书成功与 WARN 打印机缺纸的文本不包含该词，不会误计。答案唯一。
