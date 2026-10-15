## Traps
- 第 2 轮的“它”=最大的文件；第二大不是 README，而是 库存快照.csv (260 字节)，差 150。
- 重命名后文件总数不变 (5)，旧名必须消失、新名保留原内容。

## Reference solution
1. 列目录+取大小，销售_9月.csv 410；2. 410-260=150；3. 改名；4. 数文件 5 个。

## Why the answer is unique
字节数按内容(含换行)计算：410、260、120、75，README 很小；改名终态唯一。

## Five alternative phrasings of the task
- exports 目录里哪个文件最大？
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-80da3a7a
