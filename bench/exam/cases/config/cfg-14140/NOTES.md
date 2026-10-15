## Traps
- TR-DECOY: staging 段有同名键(port 8443, workers 2)；只取 prod。
- 格式: 整段回答或唯一代码块须是合法 JSON。

## Reference solution
1. 读 server.ini；2. 输出 prod 三项的 JSON。

## Why the answer is unique
prod 段 host=api.prod.internal、port=9443、workers=8。

EXAM-CANARY-b3aea087
