## Traps
- TR-DECOY: 只看最后一轮会得 1（当晚轮），只看开头的早轮会得 3；两轮合计要按横幅分好再相加。
- TR-CLAIM: 当晚轮的 SUMMARY 声称 failed=0；README 写明汇总行早于失败解析器，当晚轮正文有 1 条 FAILED 行。

## Reference solution
1. 读 README.md：两轮追加在同一份报告，最后一轮是当晚轮。
2. 检索 FAILED，在命中处附近的行段里逐条核对。
3. 按各轮 CI RUN 横幅把 FAILED 行归轮：早轮 3 条、当晚轮 1 条。
4. 合计 4 个。

## Why the answer is unique
横幅把报告切成两轮，FAILED 行各有归属；当晚汇总的声称被 README 排除。早轮 3 条加当晚 1 条，合计 4。
