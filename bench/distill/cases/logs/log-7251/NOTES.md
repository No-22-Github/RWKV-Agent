# log-7251 出题说明

## Traps
- （本题无声明陷阱，L0 基题：平实定位第一条 ERROR。）

## Reference solution
1. 读取 api-gateway.log，按时间顺序找到第一条级别为 ERROR 的记录。
2. 该记录是 08:47:21 的「POST /api/signin/batch -> 500 上游超时」，接口路径即答案。

## Why the answer is unique
08:47:21 之前只有 INFO/WARN 级别的记录，没有任何更早的 ERROR；之后虽还有三条 ERROR，但都不是「第一条」。答案只有一种读法。
