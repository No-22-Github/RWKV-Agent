## Traps
- TR-DEFN: 工具/汇总.py only adds rows whose 状态 is 入库; summing every row gives 3826.0.
- The sandbox has no python3, so running the script fails with `command not found`; the output has to be reproduced from the script's logic.

## Reference solution
1. read_file 工具/汇总.py: sums 净重克 where 状态 == 入库 over 数据/*.csv, prints kilograms with one decimal.
2. bash: `cat 数据/*.csv | awk -F, '$4=="入库" {s+=$3} END{printf "%.1f\n", s/1000}'`
Final answer: 汇总.py 会输出「入库净重合计 2699.2 千克」——环境里没有 python，我按脚本的规则（只算 状态=入库 的行）用 awk 复算得出。

## Why the answer is unique
The script's filter and rounding are explicit; returned batches are excluded.
