## Traps
- just is not installed, so `just stock` exits 127; the recipe in the justfile has to be reproduced by hand.
- TR-DECOY: 「已入库作废」 contains 「已入库」; the recipe tests equality, a substring match gives 57794.
- TR-DEFN: summing every row gives 112219.

## Reference solution
1. bash: `just stock` -> exit 127.
2. read_file justfile: the recipe is `cat 数据/*.csv | awk -F, '$2=="已入库" ...'`.
3. bash: `cat 数据/*.csv | awk -F, '$2=="已入库" {s+=$3} END{printf "%d\n", s}'`
Final answer: just stock 会输出「已入库数量合计 41379 件」（just 不可用，我按 justfile 里的配方用 awk 复算）。

## Why the answer is unique
The recipe's filter and format are explicit.

## Alternative phrasings
1. 用 just 跑一下 stock 任务，已入库的数量合计是多少件？
2. 项目的 justfile 里有个 stock 任务，执行后打印的数量告诉我。
3. 执行 just stock，把输出的入库数量合计报给我。
4. 帮我跑 justfile 的 stock，得到的已入库件数是多少？
5. just stock 会打印已入库总数，是多少？
