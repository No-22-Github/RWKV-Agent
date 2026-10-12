## Traps
- node is not installed, so `node 工具/tally.js` exits 127; the script has to be reproduced by hand.
- TR-DECOY: 「已发货退回」 contains 「已发货」; the script tests equality, a substring match gives 49322.49.
- TR-DEFN: summing every row gives 83567.70.

## Reference solution
1. bash: `node 工具/tally.js` -> exit 127.
2. read_file 工具/tally.js: sums column 3 of every 数据/*.csv where column 2 is exactly 已发货.
3. bash: `cat 数据/*.csv | awk -F, '$2=="已发货" {s+=$3} END{printf "%.2f\n", s}'`
Final answer: 工具/tally.js 会输出「已发货重量合计 32965.08 kg」（node 不可用，我按脚本逻辑用 awk 复算）。

## Why the answer is unique
The script's filter, columns and format are explicit.

## Alternative phrasings
1. 把 工具/tally.js 跑一遍，已发货的重量合计是多少 kg？
2. 工具目录里的 tally.js 会打印已发货重量，结果是多少？
3. 执行 tally.js，报一下它输出的重量合计。
4. tally.js 统计出的已发货总重量是多少公斤？
5. 运行统计脚本 tally.js，把已发货重量合计告诉我。
