## Traps
- TR-CLAIM: 末尾的 CI SUMMARY 行声称 failed=0，README 写明它出自失败解析器运行之前；正文里有 2 条 FAILED 行，涉及 2 个用例。

## Reference solution
1. 读 README.md：汇总行早于失败解析器。
2. 检索 FAILED，在命中处附近的行段里逐条核对。
3. 收集本轮的 FAILED 用例名。
4. 失败用例共 2 个。

## Why the answer is unique
README 排除了汇总行的声称，只有 FAILED 行算失败；每条 FAILED 行对应一个用例。答案是 2。
