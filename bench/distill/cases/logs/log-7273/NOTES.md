# log-7273 出题说明

## Traps
- （本题无声明陷阱，L0 基题：失败记录里直接写明了原因短语。）

## Reference solution
1. 读取 im-server.log，找到「[消息投递] 发送失败」的 ERROR 记录。
2. 冒号后写明的原因是「数据库连接池耗尽」（pool=main active=50/50），即答案。

## Why the answer is unique
全部 5 条投递失败 ERROR 写的是同一个原因「数据库连接池耗尽」，前面的两条 WARN（连接池使用率 96%/98%）也与之呼应，不存在第二种写明的原因。答案唯一。
