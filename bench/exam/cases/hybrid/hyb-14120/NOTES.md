## Traps
- TR-DECOY: prod 里还有 CONNECT_TIMEOUT_SEC=5 和 CACHE_TTL_SEC，只有 REQUEST_TIMEOUT 对应题面；复制错键会改坏 staging。
- 子任务: 读 prod 值(45)、改 staging 为 45、回答 staging 原值 10。

## Reference solution
1. 读 prod.env 得 45；2. 读 staging.env，改 REQUEST_TIMEOUT_SEC=45；3. 回答原值 10。

## Why the answer is unique
同名键唯一；staging 其余行必须原样，prod.env 不变。

## Five alternative phrasings of the task
- Make the request timeout in envs/staging.env the same as production's. Leave everything else in staging alone, and let me know what value staging was set to originally.
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)
- (non-web case: this section only satisfies lint; rephrasing does not change scoring)

EXAM-CANARY-c796df81
