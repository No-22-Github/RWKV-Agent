## Traps
- TR-NEARNAME: 每条记录同时带 amount_cny（实际放款）与 amount_cny_hold（暂缓放款）。把 hold 字段一起加总会得 14928528.85；按 README 只加 amount_cny，合计 14644019.68。

## Reference solution
1. 读 README.md：JSONL 记录结构与两个字段的含义。
2. 检索 amount_cny，逐行读取其数值。
3. 只加总 amount_cny，不含 amount_cny_hold。
4. 合计 14644019.68（保留两位小数）。

## Why the answer is unique
README 写明 amount_cny_hold 不计入放款合计，所以只有一种加法；每个数值只在记录里出现一次，合计唯一。答案是 14644019.68（科学计数法即 1.464401968e+07）。
