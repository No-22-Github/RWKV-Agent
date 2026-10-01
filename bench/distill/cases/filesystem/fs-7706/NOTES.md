## Traps
- TR-DECOY: index-2024.csv 与 index-2026.csv 文件名相近、内容同构。把两份索引的行数加在一起会报出 9 幅；README 写明对外报数只用今年索引，今年在册是 5 幅。

## Reference solution
1. 列出 patterns/：两份索引文件，文件名只差年份。
2. 读 README.md：index-2026.csv 是今年在册，index-2024.csv 是封存旧账。
3. 读 index-2026.csv：共 5 幅，蜡染 3 幅；读 index-2024.csv：旧账 4 幅。

## Why the answer is unique
诱饵 9 幅是两份索引的行数加总。README 把 index-2024.csv 定为已封存旧账、对外报数只用今年索引，加总与单看旧账都不能当作在册数；今年索引只有 5 行，工艺列里蜡染恰为 3 行。旧账行数 4 来自 index-2024.csv 自身。哪份算在册由 README 规则决定，三个事实没有第二种读法。
