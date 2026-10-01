## Traps
- TR-DECOY: recon/2025/ 下有三个名字与答案接近的文件——bank-statement-2025Q4-draft.csv（同季草稿）、bank-statement-2025Q3-final.csv（final 但上季度）、bank-statement-2024Q4-final.csv（去年）。定稿要同时满足：2025Q4、final（非 draft）。说明.md 写明 draft 是草稿、v2 后缀为准。答案文件是 bank-statement-2025Q4-final-v2.csv。

## Reference solution
1. 列出 recon/ 目录树，读到 4 份对账 CSV 与 说明.md。
2. 按说明.md 的命名口径筛选：季度=2025Q4、类型=final；draft 排除，Q3/2024 不是目标季度。
3. 2025Q4 只有一份 final（v2 后缀版本）：bank-statement-2025Q4-final-v2.csv。

## Why the answer is unique
「2025 年第四季度定稿」在命名规则下只对应一个文件：Q3 与 2024Q4 的季度不符，draft 不是定稿，同目录同名 v2 是唯一后缀版本。四个干扰文件各自至少违反一个条件，交集中只剩 bank-statement-2025Q4-final-v2.csv。
