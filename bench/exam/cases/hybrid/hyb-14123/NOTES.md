## Traps
- 每轮依赖前文: “改成”指 prod 端口；“一致”指 9443；第 4 轮问的是 staging 被改之前的 8081，文件里已无此值，只能靠对话记忆。
- 第 2、3、5 轮是写操作，不单独判分，由终态文件判分。

## Reference solution
1. 读文件答 8080；2. 改 prod 为 9443；3. 改 staging 端口 9443；4. 凭记忆答 8081；5. 改 staging retries=5。

## Why the answer is unique
终态文件整份被钉住；第 1、4 轮各有唯一数字答案(8080、8081)。

## Five alternative phrasings of the task
- conf/net.ini 里 prod 的端口现在是多少？
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-6f9c283b
